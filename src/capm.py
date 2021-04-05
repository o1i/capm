import numpy as np


def min_var_points(mus: np.array, sigma: np.ndarray, returns: np.array):
    """

    :param mus: expected returns of the instruments
    :param sigma: covariance matrix
    :param returns: returns for which to calculate the minimal variance
    :return: x and y coordinates of the min variance portfolios, portfolio weights corresponding to them and the min variance
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
    min_mus = np.matmul(np.transpose(mus), weights)  # should be returns
    min_sigmas = np.diagonal(np.matmul(np.matmul(np.transpose(weights), sigma), weights))
    return min_sigmas, returns, weights, min_mus
