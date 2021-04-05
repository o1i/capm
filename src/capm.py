import numpy as np


def min_var_points(mus: np.array, sigma: np.ndarray, riskfree: float, returns: np.array):
    """
    Calculate minimum variance portfolios and their returns.

    cf e.g. http://lists.r-forge.r-project.org/pipermail/gsoc-porta/attachments/20130712/3e2b39da/attachment-0001.pdf

    :param mus: expected returns of the instruments
    :param sigma: covariance matrix
    :param riskfree: risk free rate (needed for optimal portfolio)
    :param returns: returns for which to calculate the minimal variance
    :return: x and y coordinates of the min variance portfolios, portfolio weights corresponding to them and
             standard deviation and expected return of the tangential portfolio
    """
    sigma_inv = np.linalg.inv(sigma)
    n = sigma.shape[0]

    a = np.matmul(np.matmul(np.ones([1, n]), sigma_inv), np.ones([n, 1]))[0, 0]
    b = np.matmul(np.matmul(np.ones([1, n]), sigma_inv), mus)[0]
    c = np.matmul(np.matmul(np.transpose(mus), sigma_inv), mus)
    delta = a * c - b ** 2
    lambda1 = (c - b * returns) / delta
    lambda2 = (a * returns - b) / delta
    weights = np.matmul(sigma_inv, (np.matmul(np.ones([n, 1]), lambda1.reshape([1, -1])) +
                                    np.matmul(mus.reshape([-1, 1]), lambda2.reshape([1, -1]))))
    min_sigmas = np.diagonal(np.matmul(np.matmul(np.transpose(weights), sigma), weights))
    slopes = (np.maximum(0, returns - riskfree) / min_sigmas)[1:-1]
    tangents = np.diff((returns[1:] + returns[:-1]) / 2) / np.diff((min_sigmas[1:] + min_sigmas[:-1]) / 2)
    ind_market = np.argmin((slopes - tangents)**2)
    return min_sigmas, returns, weights, min_sigmas[ind_market + 1], returns[ind_market + 1]

