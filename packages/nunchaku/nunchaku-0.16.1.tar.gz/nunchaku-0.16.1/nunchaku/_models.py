import numpy as np


def get_phi(x, bases, sig):
    """returns matrix Phi for Eq 10."""
    # shape of matrix Phi: number of bases K * len(x)
    phi = [f(x) for f in bases]
    return np.atleast_2d(np.vstack(phi)) / sig


def A_and_mbar(phi, y, sig):
    """returns A and mbar from Eq 10."""
    y1 = np.atleast_2d(y / sig).T
    # matrix T: p * p from phi * phi
    A = phi @ phi.T
    # vector r: p * 1 from phi * y
    r = phi @ y1
    # mu: p * 1 from inv(T) * r
    mbar = np.linalg.inv(A) @ r
    return A, mbar


def general_UD(x, y, bases, sig=1):
    """returns U from Eq 12 and detA^(-1/2)."""
    p = len(bases)
    phi = get_phi(x, bases, sig)
    A, mbar = A_and_mbar(phi, y, sig)
    # U: y.T * y - mu.T * T * mu
    y1 = np.atleast_2d(y / sig).T
    U = y1.T @ y1 - mbar.T @ A @ mbar
    U = U.flatten()[0] / 2
    return U, np.linalg.det(A) ** (-1 / 2)


def logl(x, y, bases, sig, K):
    """returns the log of Eq 16."""
    N = len(x)
    U, D = general_UD(x, y, bases, sig)
    log_like = ((K - N) / 2) * np.log(2 * np.pi) - np.sum(np.log(sig)) + np.log(D) - U
    return log_like
