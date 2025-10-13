import numpy as np
import matplotlib.pyplot as plt
from logging import warning

class GibbsSampler:
    def __init__(self, nc):
        self.nc = nc

    def sample(
        self,
        numseg=3,
        initial_points="default",
        num_steps=20000,
        random_attempts=10,
        random_steps=2000,
        return_samples=False,
        check=0.5,
        lastn=100,
        plot_hist=False,
        plot_traces=True,
    ):
        """Gibbs sampler to sample the posterior.

        The sampler first sample with user-input initial guess and some
        random initial guesses in short runs and finds the one with max
        evidence, and runs a long sampling with that initial guess.
        Then, if `check` is not None, the function compares the evidence
        against that of the case where one segment is removed or two segments
        are merged.
        If the Bayes factor (more segments over fewer) is smaller than
        `check`, a warning is issued.

        Note: to find the mean and std of the boundary points, calling
        `get_boundaries()` rather than sampling from the posterior
        will be much faster.

        Parameters
        ----------
        numseg : int
            number of linear segments
        initial_points : list of int or {"default", "reverse"}
            initial guess of boundary points for the Gibbs sampler.
            If "default", start from the smallest x values;
            if "reverse", start from the largest x values.
        num_steps : int
            number of samples for a single long run of sampling
        random_attempts : int
            number of random initial guesses for short runs before the long run
        random_steps : int
            number of samples for a random short run of sampling
        return_samples : bool
            if True, return samples
        check : float or None
            threshold of Bayes factor to check if smaller number of segments
            better fits the data. If None, do not check by Bayes factor.
        lastn : int
            last n samples to be used to estimate the mean
        plot_hist : bool
            if True, plot the distribution of evidence for different random
            guesses
        plot_traces : bool
            if True, plot the traces of samples

        Raises
        ------
        ValueError
            if the initial guess input by user is not valid

        """
        # handle user input
        if initial_points is None:
            pass
        elif initial_points == "default":
            initial_start_points = np.arange(numseg, dtype=int) * self.nc.minlen
            initial_end_points = initial_start_points + self.nc.minlen - 1
            initial_points = list(
                np.stack([initial_start_points, initial_end_points]).flatten(order="F")
            )
        elif initial_points == "reverse":
            initial_start_points = np.arange(numseg, dtype=int) * self.nc.minlen
            initial_end_points = initial_start_points + self.nc.minlen - 1
            initial_points = sorted(
                len(self.nc.x)
                - np.stack([initial_start_points, initial_end_points]).flatten(
                    order="F"
                )
                - 1
            )
        elif len(initial_points) == numseg * 2:
            initial_points = [int(x) for x in initial_points]
            if not self._mc_judge(initial_points):
                raise ValueError("invalid initial points.")
        else:
            raise ValueError("len(initial_points) must equal 2 * numseg.")
        if initial_points is None:
            evi_max = -np.inf
            evi_for_plot = []
        else:
            samples_max = self._gibbs_sampler(initial_points, random_steps)
            boundaries_max = list(
                np.round(np.mean(samples_max[-lastn:], axis=0)).astype(int)
            )
            evi_max = self._gibbs_get_evidence(boundaries_max)
            evi_for_plot = [evi_max]
        # in addition to the init guess provided by user
        for j in range(random_attempts):
            init = self._gibbs_generate_initial_guess(numseg)
            samples = self._gibbs_sampler(init, random_steps)
            boundaries = list(np.round(np.median(samples[-lastn:], axis=0)).astype(int))
            evi = self._gibbs_get_evidence(boundaries)
            evi_for_plot.append(evi)
            if evi > evi_max:
                evi_max = evi
                boundaries_max = boundaries
                samples_max = samples
        # single long run
        samples_max = self._gibbs_sampler(boundaries_max, num_steps)
        boundaries_max = list(np.round(np.mean(samples_max[-100:], axis=0)).astype(int))
        if plot_hist:
            plt.figure()
            plt.hist(evi_for_plot)
            plt.ylabel("counts")
            plt.xlabel("log evidence")
            plt.show()
        if plot_traces:
            self.plot_gibbs_traces(samples_max, show=True)
        if check and self.nc.logpmc:
            self._gibbs_checker(boundaries_max, check)
        if not return_samples:
            return boundaries_max
        else:
            return boundaries_max, samples_max


    @staticmethod
    def plot_gibbs_traces(samples, show=False):
        """Plot the traces of Gibbs samples.

        Parameters
        ----------
        samples : numpy array
            samples returned by the Gibbs sampler
        show : bool
            if True, call `plt.show()`

        """

        fig, ax = plt.subplots()
        for j in range(samples.shape[1]):
            plt.plot(samples[:, j])
        ax.set_xlabel("sample number")
        ax.set_ylabel("index of boundary points")
        ax.set_ylim(-1,)
        if show:
            plt.show()
        return fig, ax


    ### Internal functions for gibbs sampling
    ###

    def _get_argmax_for_two(self):
        """find argmax of posterior for two linear segments."""
        res = self.nc.evidence.copy()
        start, end, minlen = (self.nc.start, self.nc.end, self.nc.minlen)
        results = np.empty(res.shape)
        results.fill(-np.inf)
        for st in range(start, end - minlen + 1):
            for ed in range(st + minlen, end + 1):
                res_temp = res.copy()
                res_temp[:ed, st:] = -np.inf
                results[st, ed - 1] = np.nanmax(res_temp)
        return results

    def _gibbs_sampler(self, initial_points, num_steps):
        """Gibbs sampler."""
        samples = np.zeros((num_steps, len(initial_points)), dtype=np.int16)
        # initial_points = np.asarray(initial_points)
        for i in range(num_steps):
            for j in range(len(initial_points)):
                # for x_0, ..., x_{j-1}
                x_post = list(samples[i, :j])
                # for x_{j+1}, ..., x_{n-1}
                if i == 0:
                    x_pre = initial_points[j + 1 :]
                else:
                    x_pre = list(samples[i - 1, j + 1 :])
                samples[i, j] = self._conditional_sampler(x_post, x_pre)
        return samples

    def _conditional_sampler(self, x_post, x_pre):
        """construct the conditional distribution for the Gibbs sampler."""
        all_matrix, minlen, datalen = (
            self.nc.evidence,
            self.nc.minlen,
            len(self.nc.x),
        )
        # find x_j
        index = len(x_post)
        if index == 0:
            x_post = [-1]
        if len(x_pre) == 0:
            x_pre = [datalen]
        logconditional = []
        # start point of a segment
        if index % 2 == 0:
            # find range
            xmin = x_post[-1] + 1
            xmax = x_pre[0] - minlen + 1  # inclusive
            for x in range(xmin, xmax + 1):
                logconditional.append(all_matrix[x, x_pre[0]])
        else:  # end point of a segment
            xmin = x_post[-1] + minlen - 1
            xmax = x_pre[0] - 1  # inclusive
            for x in range(xmin, xmax + 1):
                logconditional.append(all_matrix[x_post[-1], x])
        # normalise by the largest value to avoid overflow
        logconditional = logconditional - np.max(logconditional)
        conditional = np.exp(logconditional)
        # normalise to one
        conditional = conditional / np.sum(conditional)
        # generate a sample
        return int(np.random.choice(np.arange(xmin, xmax + 1), p=conditional))

    def _gibbs_generate_initial_guess(self, number):
        """generate a random initial guess for the Gibbs sampler."""
        mu, N = (self.nc.minlen, len(self.nc.x))
        res = [-1]
        for j in range(number, 0, -1):
            res.append(np.random.choice(range(res[-1] + 1, N - j * mu + 1)))
            res.append(np.random.choice(range(res[-1] + mu - 1, N - (j - 1) * mu)))
        return res[1:]

    def _gibbs_get_evidence(self, boundaries):
        """return the evidence of segments within the boundaries."""
        all_matrix = self.nc.evidence
        evi = 0
        coo = boundaries.copy()
        coo = coo[::-1]
        while len(coo) > 0:
            start = coo.pop()
            end = coo.pop()
            evi += all_matrix[start, end]
        return evi

    def _gibbs_checker(self, boundaries, check):
        """check whether a smaller number of segments has a higher evidence."""
        evi0 = self._gibbs_get_evidence(boundaries)
        evi_max = -np.inf
        boundaries_max = []
        numseg = len(boundaries) // 2
        for j in range(len(boundaries) - 1):
            boundaries_temp = boundaries.copy()
            del boundaries_temp[j : j + 2]
            evi = self._gibbs_get_evidence(boundaries_temp)
            if evi > evi_max:
                evi_max = evi
                boundaries_max = boundaries_temp
        evi_short = evi_max + self.nc._mc_logprior(len(boundaries_max))
        evi_long = evi0 + self.nc.logpmc + self.nc._mc_logprior(len(boundaries))
        log10_bayes_factor = (evi_long - evi_short) / np.log(10)
        if log10_bayes_factor < check:
            warning(
                f""" The bayes factor may favour smaller number of segments: {boundaries_max};
                log10 bayes factor ({numseg} segments over {numseg - 1}): {log10_bayes_factor}.
                or the Gibbs sampler is trapped by a local maximum or does not converge."""
            )
        else:
            print(f"Model check passed: log10 bayes factor {log10_bayes_factor}.")
        return None

    def _mc_judge(self, boundaries):
        """judge whether the given boundaries are valid."""
        minlen = self.nc.minlen
        coo = boundaries.copy()
        coo = coo[::-1]
        while len(coo) > 0:
            start = coo.pop()
            end = coo.pop()
            if end - start < minlen - 1:
                return False
        return True
