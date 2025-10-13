from ._models import logl, general_UD
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt
from logging import warning
from ._example_data import return_data
import pandas as pd
from itertools import product
from tqdm.auto import tqdm
from scipy.special import loggamma, logsumexp
from scipy.integrate import quad, simpson

# for expected behaviour: np.log(0) = -np.inf
np.seterr(divide="ignore")


class Nunchaku:
    """Find how many contiguous segments a dataset with two variables (e.g. 1D-time series) should be partitioned into,
    and find the start and end of each segment.
    The segments can be either constant, linear, or linear combinations of arbitrary basis functions (e.g. polynomials).

    Parameters
    ----------
    X : list of floats or 1-D numpy array
        the x vector of data, sorted ascendingly.
    Y : array-like
        the y vector or matrix of data, each row being one replicate of
        measurement.
    err : list of floats or 1-D numpy array, optional
        the error of the input data.
    yrange : list of length 2, optional
        the min and max of y allowed by the instrument's readout.
        Only used when `bases` is `None`.
    prior : list of length 2 or 4 or list of lists, optional
        When `bases` is `None`, the prior range of the gradient (and the intercept when length is 4).
        This argument will overwrite `yrange`.
        When `bases` is given, it is a list of lists,
        with each list being the prior range of each basis function's coefficient.
    estimate_err : bool, optional
        if True, estimate error from data; default True when Y has >= 5
        replicates.
    minlen : int, optional
        the minimal length of a valid segment (must be >= `len(bases) + 1`).
        Default value is `len(bases) + 1`.
    method : {"simpson", "quad"}, default "simpson"
        the numerical integration method to be used when error is neither
        estimated nor provided.
    bases : list of functions, optional
        the basis functions, default to be linear (`[numpy.ones_like, lambda x: x]`).
    quiet : bool, default False.
        if True, do not show progress bar.

    Raises
    ------
    ValueError
        when the length of `prior` is not 2 or 4, if provided, when `bases` is None.

    ValueError
        when the length of `prior` does not equal the length of `bases` when `bases` is given.

    Examples
    --------
    >>> from nunchaku import Nunchaku, get_example_data
    >>> x, y = get_example_data()
    >>> # load data and set the prior of the gradient
    >>> nc = Nunchaku(x, y, prior=[-5, 5])
    >>> # compare models with 1, 2, 3 and 4 linear segments
    >>> numseg, evidences = nc.get_number(num_range=(1, 4))
    >>> # get the mean and standard deviation of the boundary points
    >>> bds, bds_std = nc.get_iboundaries(numseg)
    >>> # get the information of all segments
    >>> info_df = nc.get_info(bds)
    >>> # plot the data and the segments
    >>> nc.plot(info_df)
    >>> # get the underlying piecewise function (for piecewise linear functions only)
    >>> y_prediction = nc.predict(info_df)

    """

    def __init__(
        self,
        X,
        Y,
        err=None,
        yrange=None,
        prior=None,
        estimate_err="default",
        minlen="default",
        method="simpson",
        bases=None,
        quiet=False,
    ):
        self.quiet = quiet
        # check if the input has NaN
        if np.isnan(X).any() or np.isnan(Y).any():
            raise ValueError("X or Y array contains NaN values.")
        self.x = np.asarray(X)
        self.y = np.asarray(Y)
        self.method = method
        if bases is None:
            # default linear
            self.bases = [np.ones_like, nidentity]
            self.is_linear_base = True
        else:
            self.bases = bases
            self.is_linear_base = False
        # the number of bases
        self.K = len(self.bases)
        if isinstance(err, (list, np.ndarray)):
            if np.isnan(err).any():
                raise ValueError("`err` array contains NaN values.")
            else:
                self.err = np.asarray(err)
        else:
            self.err = None
        self.start = 0
        self.end = self.x.shape[0]
        min_minlen = self.K + 1
        if minlen == "default":
            self.minlen = min_minlen
        elif minlen >= min_minlen:
            self.minlen = minlen
        else:
            warning(
                f"Nunchaku: minlen must be >= len(bases) + 1. Reset to {min_minlen}."
            )
            self.minlen = min_minlen
        # number of replicates
        if self.y.ndim == 1:
            self.nreplicates = 1
        else:
            self.nreplicates = self.y.shape[0]
        # handle estimate_err
        if estimate_err == "default":
            # if Y has 5 replicates and err is none
            if (self.y.ndim > 1) and (self.nreplicates >= 5) and (self.err is None):
                estimate_err = True
            else:
                estimate_err = False
        # if err is provided, do not estimate_err (overwrite user's setting)
        if self.err is not None:
            estimate_err = False
        # if err is not provided but Y is 1-D, impossible to estimate_err
        elif self.y.ndim == 1:
            estimate_err = False
        # now estimate err
        self.estimate_err = estimate_err
        if estimate_err:
            # x, y, instead of X, Y, are what the methods actually use
            # OK to write err because estimate_err is True only when err is None
            self.err = self.y.std(axis=0)
        # handle estimated err=0 when replicates have the same value by chance
        if self.err is not None:
            self.err[self.err == 0] = self.err[self.err > 0].mean()
        # prior
        if bases is None:
            # When it's linear
            if prior:
                if len(prior) == 2:
                    prior.append(min(-self.x[-1] * prior[1], self.x[0] * prior[0]))
                    prior.append(max(-self.x[-1] * prior[0], self.x[0] * prior[1]))
                elif len(prior) != 4:
                    raise ValueError(f"`len(prior)` should be 2 or 4, not {prior}.")
                self.prior = prior
            else:
                if yrange:
                    m_max = (yrange[1] - yrange[0]) / np.min(np.diff(self.x))
                else:
                    warning(
                        """Nunchaku: neither the prior of gradient and intercept nor the range of y is given.
                    Using the min and max of y as the range of y to estimate of prior.
                    """
                    )
                    m_max = (np.max(self.y) - np.min(self.y)) / np.min(np.diff(self.x))
                c_max = max(m_max * self.x[-1], m_max * self.x[0])
                prior = [-m_max, m_max, -c_max, c_max]
                self.prior = prior
            self.logpmc = -np.log((prior[1] - prior[0]) * (prior[3] - prior[2]))
        else:  # other bases
            if len(prior) != self.K:
                raise ValueError(
                    f"`len(prior)` must equal `len(bases)`, which is {self.K}."
                )
            prior = np.asarray(prior).flatten()
            ranges = prior[1::2] - prior[::2]
            self.logpmc = -np.sum(np.log(ranges))  # the log of Eq 8

        # pre-calculate quantities of all possible segments
        if self.err is not None:
            self.evidence = self._cal_evidence()
        else:
            self.U, self.D, self.L = self._cal_evidence()
            # handles rare cases where floating-point error leads to small negative U
            self.U[self.U < 0] = 0.0
            self.U_filled = self._matrix_fill(self.U.copy())
            if self.nreplicates > 1:
                self.sigma0 = self.y.std(axis=0).mean()
            else:
                self.sigma0 = 1

        # holder for up-coming results
        self.logZ = dict()
        self.sigma_mle = dict()

    def get_number(self, num_range):
        """Get the number of segments of the highest evidence.

        Parameters
        ----------
        num_range : int or tuple of length 2
            if integer, the range is [1, `num_range`].

        Returns
        -------
        best_numseg : int
            the number of segments with the highest evidence.
        evi : float
            log10 the model evidence of each segment number M (log10 P(D|M)).

        Raises
        ------
        OverflowError
            when numerical integration yields infinity.

        ValueError
            argument `num_range` is neither `int` nor `tuple`.

        """
        evi = []
        if isinstance(num_range, int):
            min_num = 1
            max_num = num_range
        elif isinstance(num_range, tuple):
            min_num = num_range[0]
            max_num = num_range[1]
        else:
            raise ValueError(
                f"num_range must be an int or tuple, not {type(num_range)}."
            )
        if self.err is not None:
            for M in range(min_num, max_num + 1):
                with np.errstate(divide="ignore", invalid="ignore"):
                    res = self._log_matrix_fill(self.evidence)
                    evi_M = (
                        self._findZ_sigma(sigma=None, number=M, matrix=res)
                        + self._mc_logprior(M)
                        + self.logpmc * M
                    ) / np.log(10)
                evi.append(evi_M)
        else:
            for M in tqdm(
                range(min_num, max_num + 1),
                desc="getting model evidence",
                disable=self.quiet,
            ):
                with np.errstate(divide="ignore", invalid="ignore"):
                    if M > 2:
                        logZ = self._findZ_unknown_err_numerical(M, method=self.method)
                        self.logZ[M] = logZ  # store Z for finding iboundaries
                        log_evi = logZ + (
                            -len(self.x) * self.nreplicates / 2 + M * self.K / 2
                        ) * np.log(2 * np.pi)
                    else:  # use analytical sum where possible
                        logZ = self._findZ_unknown_err_analytical(M)
                        self.logZ[M] = logZ
                        log_evi = (
                            logZ
                            + loggamma(
                                (len(self.x) * self.nreplicates - 1 - self.K * M) / 2
                            )
                            + (-len(self.x) * self.nreplicates / 2 + M * self.K / 2)
                            * np.log(2 * np.pi)
                        )
                    evi_M = (
                        +log_evi + self._mc_logprior(M) + self.logpmc * M
                    ) / np.log(10)
                evi.append(evi_M)
            if not np.any(np.isfinite(np.array(evi))):
                OverflowError("Nunchaku: the evidence may be numerically too small.")
        ind = np.nanargmax(evi)
        best_numseg = ind + min_num
        # check
        if best_numseg == max_num:
            warning(
                "Nunchaku: the best number of segments equals the largest candidate."
            )
        return best_numseg, evi

    def get_info(self, boundaries):
        """Return a Pandas dataframe that describes the segments within given internal boundaries,
        returned by `get_iboundaries()`.

        Parameters
        ----------
        boundaries : list of int
            a list of indices of boundary points

        Returns
        -------
        df : pd.Dataframe
            Pandas dataframe that describes the segments within given internal boundaries,

        """
        # quick check to make sure boundaries are sensible
        x, y = (self.x, self.y)
        keys = [
            "start",
            "end",
            "gradient",
            "intercept",
            "rsquare",
            "x range",
            "y range",
            "delta x",
            "delta y",
        ]
        d = {k: [] for k in keys}
        d["start"] = [0] + list(map(lambda x: x + 1, boundaries))
        d["end"] = boundaries + [len(self.x) - 1]
        for st, ed in zip(d["start"], d["end"]):
            if y.ndim > 1:
                # flatten for regression
                x_flat = np.append([], [x[st : ed + 1]] * self.nreplicates)
                y_flat = y[:, st : ed + 1].flatten(order="C")
                y_mn = y[:, st : ed + 1].mean(axis=0)
            else:
                x_flat = x[st : ed + 1]
                y_flat = y[st : ed + 1]
                y_mn = y[st : ed + 1]
            d["x range"].append((x_flat[0], x_flat[-1]))
            d["y range"].append((y_mn[0], y_mn[-1]))
            d["delta x"].append(x_flat[-1] - x_flat[0])
            d["delta y"].append(y_mn[-1] - y_mn[0])
            lin_res = linregress(x_flat, y_flat)
            d["gradient"].append(lin_res.slope)
            d["intercept"].append(lin_res.intercept)
            d["rsquare"].append(lin_res.rvalue**2)
        return pd.DataFrame(d)

    def get_iboundaries(self, numseg, round=True, bd_err=True):
        """Return the mean and standard deviation of the internal boundary indices,
        i.e. excluding the first (0) and last (`len(x)`) indices of the data.

        Parameters
        ----------
        numseg : int
            number of segments
        round : bool, default True
            whether to round the returned mean to integer
        bd_err : bool, default True
            whether to estimate the error of the boundary positions. Setting it to False
            will reduce the computational load.

        Returns
        -------
        boundaries : list of int or float
            Indices of internal boundaries
        boundaries_err : list of float
            Error of the indices of internal boundaries

        Raises
        ------
        OverflowError
            when numerical integration yields infinity.

        """
        boundaries = []
        boundaries_err = []
        if self.err is not None:
            res = self._log_matrix_fill(self.evidence)
            logZ = self._findZ_sigma(sigma=None, number=numseg, matrix=res)
            for j in range(1, numseg):
                coo = np.exp(
                    self._find_moment_sigma(sigma=None, number=numseg, k=j, matrix=res)
                    - logZ
                )
                boundaries.append(coo)
                if bd_err:
                    coo2 = np.exp(
                        self._find_moment_sigma(
                            sigma=None, number=numseg, k=j, moment=2, matrix=res
                        )
                        - logZ
                    )
                    var = coo2 - coo**2
                    if var >= 0:
                        boundaries_err.append(np.sqrt(var))
                    else:
                        boundaries_err.append(np.nan)
                        warning(
                            f"""Nunchaku: get negative variance value for the {j}-th iboundary. Returned NaN for this iboundary's error.
                            The variance value is {var}: if it's close to zero, this arises from floating-point errors and can be deemed zero."""
                        )
        else:
            if numseg > 2:
                for j in tqdm(
                    range(1, numseg),
                    desc="getting internal boundaries",
                    disable=self.quiet,
                ):
                    coo = np.exp(
                        self._find_moment_unknown_err_numerical(
                            numseg, j, method=self.method
                        )
                        - self.logZ[numseg],
                    )
                    # quick check
                    if coo >= self.minlen and coo < len(self.x):
                        pass
                    else:
                        warning(
                            f"Nunchaku: Integral may be inaccurate for the {j}-th boundary point."
                        )
                    boundaries.append(coo)
                    if bd_err:
                        coo2 = np.exp(
                            self._find_moment_unknown_err_numerical(
                                numseg, j, moment=2, method=self.method
                            )
                            - self.logZ[numseg],
                        )
                        var = coo2 - coo**2
                        if var >= 0:
                            boundaries_err.append(np.sqrt(var))
                        else:
                            boundaries_err.append(np.nan)
                            warning(
                                f"""Nunchaku: get negative variance value for the {j}-th iboundary. Returned NaN for this iboundary's error.
                                The variance value is {var}: if it's close to zero, this arises from floating-point errors and can be deemed zero."""
                            )
            else:
                for j in tqdm(
                    range(1, numseg),
                    desc="getting internal boundaries",
                    disable=self.quiet,
                ):
                    coo = np.exp(
                        self._find_moment_unknown_err_analytical(numseg, j)
                        - self.logZ[numseg],
                    )
                    boundaries.append(coo)
                    if bd_err:
                        coo2 = np.exp(
                            self._find_moment_unknown_err_analytical(
                                numseg, j, moment=2
                            )
                            - self.logZ[numseg],
                        )
                        var = coo2 - coo**2
                        if var >= 0:
                            boundaries_err.append(np.sqrt(var))
                        else:
                            boundaries_err.append(np.nan)
                            warning(
                                f"""Nunchaku: get negative variance value for the {j}-th iboundary. Returned NaN for this iboundary's error.
                                The variance value is {var}: if it's close to zero, this arises from floating-point errors and can be deemed zero."""
                            )

        if round:
            return list(np.array(boundaries).astype(int)), boundaries_err
        else:
            return boundaries, boundaries_err

    def plot(
        self,
        info_df=None,
        show=False,
        start=True,
        end=True,
        figsize=(6, 5),
        err_width=1,
        s=50,
        color="red",
        alpha=0.5,
        hlmax={"rsquare": ("orange", "s")},
        hlmin=None,
        **kwargs,
    ):
        """Plot the raw data and the start and/or end points of each segment,
        and highlight the linear segments of interest if the model is piece-wise linear.

        Parameters
        ----------
        info_df : pandas.DataFrame, default None
            the pandas dataframe returned by `get_info()`; if None, only the data is shown.
        show : bool, default False
            if True, call `plt.show()`
        start : bool, default True
            if True, show the start point of each segment
        end : bool, default True
            if True, show the end point of each segment
        figsize : tuple, default (6, 5)
            size of figure passed to `plt.subplots()`
        s : float, default 50
            size of the boundary points as passed into Matplotlib's `scatter()`
        color : str, default "red"
            color of the boundary points and segments as passed into Matplotlib's `scatter()` and `plot()`
        alpha : float, default 0.5
            transparency of the boundary points and segments as passed into Matplotlib's `scatter()` and `plot()`
        hlmax : dict, default {"rsquare": ("orange", "s")}
            highlighting the linear segment with max quantity (e.g. rsquare).
            The key is the column name in `info_df` and the value is a tuple: (color, marker).
            This argument has no effect if the segments are not linear.
        hlmin : dict, optional
            highlighting the linear segment with min quantity (e.g. rsquare).
            The key is the column name in `info_df` and the value is a tuple: (color, marker).
            This argument has no effect if the segments are not linear.
        **kwargs : keyword arguments
            keyword arguments to be passed into Matplotlib's `scatter()`

        Returns
        -------
        fig : `matplotlib.figure.Figure` object
            Matplotlib Figure object
        axes : `matplotlib.axes.Axes` object
            Matplotlib Axes object

        """

        fig, ax = plt.subplots(figsize=figsize)

        # plot raw data
        ax.plot(self.x, self.y.T, color="grey", alpha=0.5)

        # find highlighted segments
        if (info_df is not None) and self.is_linear_base:
            # handle how to highlight segments
            if hlmax is not None:
                idx_ignore_max = [info_df[k].idxmax() for k in hlmax.keys()]
                idx_color_max = [v[0] for v in hlmax.values()]
                idx_marker_max = [v[1] for v in hlmax.values()]
            else:
                idx_ignore_max = []
                idx_color_max = []
                idx_marker_max = []

            if hlmin is not None:
                idx_ignore_min = [info_df[k].idxmin() for k in hlmin.keys()]
                idx_color_min = [v[0] for v in hlmin.values()]
                idx_marker_min = [v[1] for v in hlmin.values()]
            else:
                idx_ignore_min = []
                idx_color_min = []
                idx_marker_min = []

            idx_ignore = idx_ignore_max + idx_ignore_min
            idx_color = idx_color_max + idx_color_min
            idx_marker = idx_marker_max + idx_marker_min

            for j in range(info_df.shape[0]):
                if j not in idx_ignore:
                    bd_start = info_df.loc[j, "start"]
                    bd_end = info_df.loc[j, "end"]
                    slope = info_df.loc[j, "gradient"]
                    intercept = info_df.loc[j, "intercept"]
                    y_start = slope * self.x[bd_start] + intercept
                    y_end = slope * self.x[bd_end] + intercept
                    # plot the line
                    ax.plot(
                        [self.x[bd_start], self.x[bd_end]],
                        [y_start, y_end],
                        color=color,
                        alpha=alpha,
                        marker="",
                    )
                    # plot the starting point
                    if start:
                        ax.scatter(
                            self.x[bd_start],
                            y_start,
                            color=color,
                            alpha=alpha,
                            marker="o",
                            s=s,
                            **kwargs,
                        )
                    # plot the end point
                    if end:
                        ax.scatter(
                            self.x[bd_end],
                            y_end,
                            color=color,
                            alpha=alpha,
                            marker="o",
                            s=s,
                            **kwargs,
                        )
            for idx, cl, mk in zip(idx_ignore, idx_color, idx_marker):
                bd_start = info_df.loc[idx, "start"]
                bd_end = info_df.loc[idx, "end"]
                slope = info_df.loc[idx, "gradient"]
                intercept = info_df.loc[idx, "intercept"]
                y_start = slope * self.x[bd_start] + intercept
                y_end = slope * self.x[bd_end] + intercept
                # plot the line
                ax.plot(
                    [self.x[bd_start], self.x[bd_end]],
                    [y_start, y_end],
                    color=cl,
                    alpha=alpha,
                    marker="",
                )
                # plot the starting point
                if start:
                    ax.scatter(
                        self.x[bd_start],
                        y_start,
                        color=cl,
                        alpha=alpha,
                        marker=mk,
                        s=s,
                        **kwargs,
                    )
                # plot the end point
                if end:
                    ax.scatter(
                        self.x[bd_end],
                        y_end,
                        color=cl,
                        alpha=alpha,
                        marker=mk,
                        s=s,
                        **kwargs,
                    )
        elif info_df is not None:  # if the model is not linear
            for j in range(info_df.shape[0]):
                bd_start = info_df.loc[j, "start"]
                bd_end = info_df.loc[j, "end"]
                y = self.y.mean(axis=0)
                # plot the starting point
                if start:
                    ax.scatter(
                        self.x[bd_start],
                        y[bd_start],
                        color=color,
                        alpha=alpha,
                        marker="o",
                        linestyle="",
                        s=s,
                        **kwargs,
                    )
                # plot the end point
                if end:
                    ax.scatter(
                        self.x[bd_end],
                        y[bd_end],
                        color=color,
                        alpha=alpha,
                        marker="o",
                        linestyle="",
                        s=s,
                        **kwargs,
                    )
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        if show:
            plt.show(block=False)
        return fig, ax

    ### Internal functions

    def _cal_evidence(self):
        """Return the log of Eq 9 for each possible segment between start and end,
        when sigma is known. Otherwise calculate U, detA^(-1/2) and (N_r ell) for Eq 21.
        """
        X, Y, err, start, end, minlen = (
            self.x,
            self.y,
            self.err,
            self.start,
            self.end,
            self.minlen,
        )
        if self.err is None:
            results_U = np.ones((len(X), len(X))) * np.nan
            results_D = np.ones((len(X), len(X))) * np.nan
            results_L = np.ones((len(X), len(X))) * np.nan
            for st in tqdm(
                range(start, end - minlen + 1),
                desc="getting evidence matrix",
                disable=self.quiet,
            ):
                for ed in range(st + minlen, end + 1):
                    evi_u, evi_d = self._cal_evidence_unknown_err(st, ed)
                    results_U[st, ed - 1] = evi_u
                    results_D[st, ed - 1] = evi_d
                    results_L[st, ed - 1] = (ed - st) * self.nreplicates
            return results_U, results_D, results_L
        else:
            results = np.ones((len(X), len(X))) * np.nan
            for st in range(start, end - minlen + 1):
                for ed in range(st + minlen, end + 1):
                    evi = self._cal_evidence_known_error(st, ed)
                    # unknown bug in either builtin sum or numpy sum
                    if evi > 9e8:
                        evi = -np.inf
                    results[st, ed - 1] = evi
            return results

    def _cal_evidence_unknown_err(self, start, end):
        """return U and (detA)^(-1/2) in Eq 21 for all possible segments.

        Parameters
        ----------
        start : init
            start of segment
        end : int
            end of segment (exclusive)

        """
        func = general_UD
        X, Y, nreps = (self.x, self.y, self.nreplicates)
        bases = self.bases
        # flatten multiple reps
        if Y.ndim > 1:
            X_flat = np.append([], [X[start:end]] * nreps)  # flatten X
            Y_flat = Y[:, start:end].flatten(order="C")
            # n_flat = len(X[start:end]) * nreps
        else:
            X_flat = X[start:end]
            Y_flat = Y[start:end]
            # n_flat = len(X[start:end])
        return func(X_flat, Y_flat, bases)

    def _cal_evidence_known_error(self, start, end):
        """return log of Eq 9 through Eq 16.

        Parameters
        ----------
        start : init
            start of segment
        end : int
            end of segment (exclusive)

        """
        func = logl
        X, Y, err, nreps = (self.x, self.y, self.err, self.nreplicates)
        bases = self.bases
        # flatten multiple reps
        if Y.ndim > 1:
            X_flat = np.append([], [X[start:end]] * nreps)  # flatten X
            err_flat = np.append([], [err[start:end]] * nreps)  # flatten err
            Y_flat = Y[:, start:end].flatten(order="C")
            # n_flat = len(X[start:end]) * nreps
        else:
            X_flat = X[start:end]
            Y_flat = Y[start:end]
            err_flat = err[start:end]
            # n_flat = len(X[start:end])
        return func(X_flat, Y_flat, bases, err_flat, self.K)

    def _mc_logprior(self, numseg):
        """return the log of Eq 4 given the number of segments (M)."""
        if self.err is not None:
            res = self.evidence.copy()
        else:
            res = self.D.copy()
        res[~np.isnan(res)] = 0
        res[np.isnan(res)] = -np.inf
        return -self._findZ_sigma(sigma=None, number=numseg, matrix=res)

    def _findZ_unknown_err_analytical(self, number):
        """Return the sum and integral of Eq 23, in which
        the 2pi term and the Gamma function are handled in get_number().
        """
        exp_u = self._matrix_fill(self.U.copy())
        exp_d = self._matrix_fill(self.D.copy())
        N = len(self.x)
        M = number
        minlen = self.minlen
        # upper limits of (number - 1) iboundries
        u_limits = [N - k * minlen for k in range(number - 1, 0, -1)]
        l_limits = minlen - 1
        # list of possible values of each iboundary (end point)
        ib_ranges = [range(l_limits, u) for u in u_limits]
        all_combs = product(*ib_ranges)
        # calculate sum
        evi = 0
        for ibs in all_combs:
            # including start and end
            begs_minus_1 = [-1] + list(ibs)
            ends = list(ibs) + [N - 1]
            d_i = np.array([exp_d[b + 1, e] for b, e in zip(begs_minus_1, ends)])
            D = np.prod(d_i)
            u_i = np.array([exp_u[b + 1, e] for b, e in zip(begs_minus_1, ends)])
            U = np.sum(u_i)
            # some constants like 2pi and gamma are handled in get_numbers()
            evi += D * U ** ((self.K * M + 1 - N * self.nreplicates) / 2) / 2
        return np.log(evi)

    @staticmethod
    def _matrix_fill(matrix):
        """replace matrix nans with zeros."""
        matrix[np.isnan(matrix)] = 0
        return matrix

    @staticmethod
    def _log_matrix_fill(matrix):
        """replace matrix nans with `-np.inf`."""
        matrix[np.isnan(matrix)] = -np.inf
        return matrix

    def _log_eq21(self, sigma):
        """
        return Eq 21 for each possible segment given sigma.

        the 2pi term is left out for `get_number()` to handle.
        """
        return -(self.U) / sigma**2 + (self.K - self.L) * np.log(sigma) + np.log(self.D)

    def _findZ_sigma(self, sigma, number, matrix=None, vec=None):
        """Return the sum in Eq 23 given sigma, through Eqs 21 and 22.
        When sigma is None (i.e. given and absorbed inside matrix), return the sum in Eq 8.
        """
        if matrix is None:
            matrix = self._log_matrix_fill(self._log_eq21(sigma))
        datalen = len(self.x)
        if vec is None:
            if number == 1:
                return matrix[0, -1]
            else:
                f_M = np.full(datalen, -np.inf)
                f_M[:-1] = matrix[1:, datalen - 1]
                return self._findZ_sigma(sigma, number - 1, matrix, f_M)
        else:
            if number == 1:
                return log_matmul(matrix[[0]], np.atleast_2d(vec).T)[0, 0]
            else:
                f_M = np.full(datalen, -np.inf)
                f_M[:-1] = log_matmul(matrix, np.atleast_2d(vec).T).flatten()[1:]
                return self._findZ_sigma(sigma, number - 1, matrix, f_M)

    def _find_moment_sigma(self, sigma, number, k, moment=1, matrix=None, vec=None):
        """Return the sum in Eq 19 given sigma.
        When sigma is None, it's given and absorbed inside matrix.
        """
        if matrix is None:
            matrix = self._log_matrix_fill(self._log_eq21(sigma))
        datalen = len(self.x)
        if vec is None:
            if number == 1:
                return None
            else:  # k < number when vec is None
                f_M = np.full(datalen, -np.inf)
                f_M[:-1] = matrix[1:, datalen - 1]
                return self._find_moment_sigma(
                    sigma, number - 1, k, moment, matrix, f_M
                )
        else:
            if number == 1:
                if k == number:
                    return log_matmul(
                        matrix[[0]],
                        np.atleast_2d(vec).T
                        + np.atleast_2d(np.log(np.arange(datalen))).T * moment,
                    )[0, 0]
                else:
                    return log_matmul(matrix[[0]], np.atleast_2d(vec).T)[0, 0]
            else:
                f_M = np.full(datalen, -np.inf)
                if k == number:
                    f_M[:-1] = log_matmul(
                        matrix,
                        np.atleast_2d(vec).T
                        + np.atleast_2d(np.log(np.arange(datalen))).T * moment,
                    ).flatten()[1:]
                else:
                    f_M[:-1] = log_matmul(matrix, np.atleast_2d(vec).T).flatten()[1:]
                return self._find_moment_sigma(
                    sigma, number - 1, k, moment, matrix, f_M
                )

    def _find_moment_unknown_err_analytical(self, number, k, moment=1):
        """Return the equivalent of the sum Eq 19 with sigma marginalised.
        the 2pi term and the Gamma Function are ignored:
        that's ok because `_findZ_unknown_err_analytical()` have the same terms ignored.
        """
        exp_u = self._matrix_fill(self.U.copy())
        exp_d = self._matrix_fill(self.D.copy())
        N = len(self.x)
        M = number
        minlen = self.minlen
        # upper limits of (number - 1) iboundries
        u_limits = [N - j * minlen for j in range(number - 1, 0, -1)]
        l_limits = minlen - 1
        # list of possible values of each iboundary (end point)
        ib_ranges = [range(l_limits, u) for u in u_limits]
        all_combs = product(*ib_ranges)
        # calculate sum
        evi = 0
        for ibs in all_combs:
            # including start and end
            begs_minus_1 = [-1] + list(ibs)
            ends = list(ibs) + [N - 1]
            d_i = np.array([exp_d[b + 1, e] for b, e in zip(begs_minus_1, ends)])
            D = np.prod(d_i)
            u_i = np.array([exp_u[b + 1, e] for b, e in zip(begs_minus_1, ends)])
            U = np.sum(u_i)
            evi += (
                D
                * U ** ((M * self.K + 1 - N * self.nreplicates) / 2)
                / 2
                # * gamma((N - 1) / 2 - M)
                * ibs[k - 1] ** moment
            )
        return np.log(evi)

    def _findZ_unknown_err_numerical(self, number, method="simpson"):
        """Return the sum and integral in Eq 23."""
        sigma_mle = self._find_sigma_by_EM(number)
        # store sigma_mle for finding iboundaries
        self.sigma_mle[number] = sigma_mle
        if np.isfinite(sigma_mle):
            lognorm = self._findZ_sigma(sigma_mle, number)
        else:
            lognorm = 0
        if np.isfinite(lognorm):
            integrand = lambda sigma, M: np.exp(self._findZ_sigma(sigma, M) - lognorm)
        else:
            raise OverflowError("Failed the find the normalisation factor.")
        if method == "quad" or np.isnan(sigma_mle):
            # if MLE of sigma is nan, fall back to quad
            res = quad(
                integrand,
                0,
                np.inf,
                args=(number,),
                epsabs=0.0,
                epsrel=1e-10,
            )
        elif method == "simpson":
            low = sigma_mle / 10
            high = sigma_mle * 10
            x1 = np.logspace(np.log10(low), np.log10(sigma_mle), 100)
            x2 = np.logspace(np.log10(sigma_mle), np.log10(high), 100)
            itg_vec = np.vectorize(integrand)
            y1 = itg_vec(x1, number)
            y2 = itg_vec(x2, number)
            res = simpson(y1, x=x1) + simpson(y2, x=x2)
            res = (res, 0.0)
        if np.isfinite(res[0]):
            if res[0] <= res[1]:
                warning(
                    f"Nunchaku: Integral may be inaccurate when finding model evidence with {number} segments."
                )
            return np.log(res[0]) + lognorm
        elif np.isnan(res[0]):
            warning(
                f"Nunchaku: Integration failed when finding model evidence with {number} segments. Returned NaN for evidence."
            )
            return np.nan
        else:
            raise OverflowError("Integral is too large when finding model evidence.")

    def _find_moment_unknown_err_numerical(self, number, k, moment=1, method="simpson"):
        """Return the equivalent of the sum in Eq 19 with sigma marginalised."""
        sigma_mle = self.sigma_mle[number]
        if np.isfinite(sigma_mle):
            lognorm = self._find_moment_sigma(sigma_mle, number, k, moment)
        else:
            lognorm = 0
        if np.isfinite(lognorm):
            integrand = lambda sigma, M, k, mom: np.exp(
                self._find_moment_sigma(sigma, M, k, mom) - lognorm
            )
        else:
            raise OverflowError("Integrand is too large when finding moment.")
        if method == "quad" or np.isnan(sigma_mle):
            # if MLE of sigma is nan, fall back to quad
            res = quad(
                integrand,
                0,
                np.inf,
                args=(number, k, moment),
                epsabs=0.0,
                epsrel=1e-10,
            )
        elif method == "simpson":
            low = sigma_mle / 10
            high = sigma_mle * 10
            x1 = np.logspace(np.log10(low), np.log10(sigma_mle), 100)
            x2 = np.logspace(np.log10(sigma_mle), np.log10(high), 100)
            itg_vec = np.vectorize(integrand)
            y1 = itg_vec(x1, number, k, moment)
            y2 = itg_vec(x2, number, k, moment)
            res = simpson(y1, x=x1) + simpson(y2, x=x2)
            res = (res, 0.0)
        if np.isfinite(res[0]):
            if res[0] <= res[1]:
                warning("Nunchaku: Integral may be inaccurate when finding moment.")
            return np.log(res[0]) + lognorm
        elif np.isnan(res[0]):
            raise OverflowError("Integration failed when finding boundary points.")
        else:
            raise OverflowError("Integral is too large when finding boundary points.")

    def _find_expectation_sigma_by_segment(
        self, sigma, number, k, matrix=None, vec=None
    ):
        """return (E[U_i] in Eq 25) * (the sum over n in Eq 23) given sigma = sigma_0.
        similar to calculating E[n_i] in Eq 19."""
        if matrix is None:
            matrix = self._log_matrix_fill(self._log_eq21(sigma))
        Umat = np.log(self.U_filled)
        datalen = len(self.x)
        if vec is None:
            if number == 1:
                # then k must be 1.
                return matrix[0, -1] + Umat[0, -1]
            else:
                if k == number:  # the last segment
                    f_M = np.full(datalen, -np.inf)
                    f_M[:-1] = matrix[1:, datalen - 1] + Umat[1:, datalen - 1]
                    return self._find_expectation_sigma_by_segment(
                        sigma, number - 1, k, matrix, f_M
                    )
                else:
                    f_M = np.full(datalen, -np.inf)
                    f_M[:-1] = matrix[1:, datalen - 1]
                    return self._find_expectation_sigma_by_segment(
                        sigma, number - 1, k, matrix, f_M
                    )
        else:
            if number == 1:
                if k == 1:  # the first segment
                    return log_matmul(matrix[[0]] + Umat[[0]], np.atleast_2d(vec).T)[
                        0, 0
                    ]
                else:
                    return log_matmul(matrix[[0]], np.atleast_2d(vec).T)[0, 0]
            else:
                f_M = np.full(datalen, -np.inf)
                if k == number:
                    f_M[:-1] = log_matmul(
                        matrix + Umat, np.atleast_2d(vec).T
                    ).flatten()[1:]
                else:
                    f_M[:-1] = log_matmul(matrix, np.atleast_2d(vec).T).flatten()[1:]
                return self._find_expectation_sigma_by_segment(
                    sigma, number - 1, k, matrix, f_M
                )

    def _find_expectation_sigma(self, sigma0, number):
        """return sigma_n of Eq 25."""
        logE_segments = [
            self._find_expectation_sigma_by_segment(sigma0, number, k)
            for k in range(1, number + 1)
        ]
        logE = logsumexp(logE_segments)
        # Z given sigma0
        logZ = self._findZ_sigma(sigma=sigma0, number=number)
        N = len(self.x) * self.nreplicates
        # return np.sqrt(E / Z / (N - self.K * number) * 2)
        return np.exp(0.5 * (logE - logZ - np.log(N - self.K * number) + np.log(2)))

    def _find_sigma_by_EM(self, number, reltol=1e-5, max_attempt=100):
        """Calculate Eq 24 starting from an initial guess sigma0 and then iterate to update."""
        sigma0s = [self.sigma0, 0.1, 1, 10, 100]
        for s in sigma0s:
            sigma0 = s
            for j in range(max_attempt):
                sigma = self._find_expectation_sigma(sigma0, number)
                if np.isnan(sigma):
                    # if estimation fails, start from a different value
                    break
                reldiff = np.abs(sigma - sigma0) / sigma0
                if reldiff < reltol:
                    # for some reason sigma is float128 if not converted
                    return float(sigma)
                else:
                    sigma0 = sigma
            else:
                warning(
                    f"""Nunchaku: EM algorithm does not yet converge after {max_attempt} attempts.
                    Current relative difference: {reldiff}."""
                )
                return float(sigma)
        # if the above loop never returns, EM failed
        warning(
            f"Nunchaku: failed to estimate MLE of sigma when the number of segments is {number}."
        )
        return np.nan

    def get_MLE_of_error(self, numseg):
        """Returns the MLE of the data's error estimated by expectation-maximisation.

        Parameters
        ----------
        numseg : int
            number of segments

        Returns
        -------
        err : float
            The MLE of the data's error, assuming homogeneity of variance.

        Raises
        ------
        NotImplementedError
            when the error is already provided or estimated.

        """
        if self.err is not None:
            raise NotImplementedError(
                "MLE of error is only available when error is neither provided nor estimated."
            )
        else:
            return self._find_sigma_by_EM(numseg)

    def predict(self, info_df):
        """Returns the estimated piecewise-linear function.
        Note: this function only works when the model is piece-wise linear.

        Parameters
        ----------
        info_df : pandas.DataFrame
            the pandas dataframe returned by `get_info()`.

        Returns
        -------
        y_preds : numpy.ndarray
            the estimated piecewise-linear function.
        """

        y_preds = []
        for _, r in info_df.iterrows():
            i1 = r["start"]
            i2 = r["end"] + 1
            m = r["gradient"]
            c = r["intercept"]
            xs = self.x[i1:i2]
            y_preds.append(m * xs + c)
        y_preds = np.concatenate(y_preds, axis=None)
        return y_preds


def log_matmul(A, B):
    """see https://stackoverflow.com/questions/36467022/handling-matrix-multiplication-in-log-space-in-python"""
    Astack = np.stack([A] * B.shape[1]).transpose(1, 0, 2)
    Bstack = np.stack([B] * A.shape[0]).transpose(0, 2, 1)
    return logsumexp(Astack + Bstack, axis=2)


def nidentity(x):
    """identity function."""
    return x


def get_example_data(plot=False):
    """Return example data, with x being cell number and y being three replicates of OD measurement.

    Parameters
    ----------
    plot : bool, default False
        If true, plot the example data.

    Returns
    -------
    x : 1D numpy array
        Example data of x
    y : 2D numpy array
        Example data of y

    Examples
    --------
    >>> from nunchaku.nunchaku import get_example_data
    >>> x, y = get_example_data()
    """
    x, y = return_data()
    if plot:
        fig, ax = plt.subplots()
        for j in range(y.shape[0]):
            ax.scatter(x, y[j, :], alpha=0.7, color="b")
        ax.set_xlabel("cell number")
        ax.set_ylabel("optical density (OD)")
        plt.show()
    return x, y
