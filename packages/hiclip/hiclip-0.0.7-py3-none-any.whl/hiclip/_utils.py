import logging
from math import log10, sqrt

import numpy as np
import torch
from numpy.fft import fft2, ifft2, ifftshift
from scvi import scvi_logger, settings

"""
Hi-C matrix transformation
"""


def tensor2mat(tensor: torch.Tensor) -> torch.Tensor:
    len_sqrt = int(sqrt(tensor.size()[-1]))
    new_x_shape = tensor.size()[:-1] + (len_sqrt, len_sqrt)
    tensor = tensor.view(*new_x_shape)

    return tensor


"""
Coarsen the matrix.
"""


def _fftblur(img, sigma):
    h, w = img.shape

    X, Y = np.meshgrid(np.arange(w), np.arange(h))
    X, Y = X - w // 2, Y - h // 2
    Z = np.exp(-0.5 * (X**2 + Y**2) / (sigma**2))
    Z = Z / Z.sum()

    out = ifftshift(ifft2(fft2(img) * fft2(Z)))
    return out


def _fan(sparse_mat, mask):
    N = np.prod(mask.shape)
    num_kept = np.nonzero(mask)[0].shape[0]
    sigma = sqrt(N / (np.pi * num_kept))

    c = _fftblur(sparse_mat, sigma)
    i = _fftblur(mask, sigma)

    mat = np.abs(c / i)
    return mat


def _sparsify(mat, sparse_mat, span):
    h, w = mat.shape
    for i in range(0, h, span):
        for j in range(0, w, span):
            tmp = mat[i : i + span, j : j + span].mean()
            _x, _y = i + span / 2, j + span / 2
            _length = max(abs(_x - _y), 1)
            tmp *= max(log10(_length), 1)
            sparse_mat[i : i + span, j : j + span] += tmp
    return sparse_mat


def coarsen(mat, spans=[5, 10]):
    mask = np.ones(mat.shape)
    sparse_mat = np.zeros(mat.shape)

    spans.sort(reverse=True)
    for span in spans:
        sparse_mat = _sparsify(mat, sparse_mat, span)

    return _fan(sparse_mat, mask)


"""
metric
"""


def hiclip_metric(
    l1_loss: float,
    perceptual_loss: float,
) -> float:
    return np.nanmean([l1_loss, perceptual_loss])


"""
log
"""

_logger = scvi_logger
settings.logging_dir = "./.hiclip/"
