# Copyright 2025 Artezaru
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy
from numbers import Integral, Real
from typing import Sequence, List, Optional

from .core.core_polynomial import core_polynomial

def zernike_polynomial(
    rho: numpy.ndarray, 
    theta: numpy.ndarray,
    n: Sequence[Integral],
    m: Sequence[Integral],
    rho_derivative: Optional[Sequence[Integral]] = None,
    theta_derivative: Optional[Sequence[Integral]] = None,
    default: Real = numpy.nan,
    precompute: bool = True,
    _skip: bool = False
) -> List[numpy.ndarray]:
    r"""
    Computes the Zernike polynomial :math:`Z_{n}^{m}(\rho, \theta)` for :math:`\rho \leq 1` and :math:`\theta \in [0, 2\pi]`.

    The Zernike polynomial is defined as follows:

    .. math::

        Z_{n}^{m}(\rho, \theta) = R_{n}^{m}(\rho) \cos(m \theta) \quad \text{if} \quad m \geq 0

    .. math::

        Z_{n}^{m}(\rho, \theta) = R_{n}^{-m}(\rho) \sin(-m \theta) \quad \text{if} \quad m < 0

    If :math:`n < 0`, :math:`n < |m|`, or :math:`(n - m)` is odd, the output is a zeros array with the same shape as :math:`\rho`.
    If :math:`\rho` is not in :math:`0 \leq \rho \leq 1` or :math:`\rho` is numpy.nan, the output is set to the default value (numpy.nan by default).

    .. seealso::

        - :func:`pyzernike.radial_polynomial` for computing the radial part of the Zernike polynomial :math:`R_{n}^{m}(\rho)`.
        - :func:`pyzernike.core.core_polynomial` to inspect the core implementation of the computation.
        - The page :doc:`../../mathematical_description` in the documentation for the detailed mathematical description of the Zernike polynomials.
    
    This function allows to compute several Zernike polynomials at once for different sets of (order, degree, derivative orders) given as sequences,
    which can be more efficient than calling the polynomial function multiple times.

    - The parameters ``rho`` and ``theta`` must be numpy arrays of the same shape.
    - The parameters ``n``, ``m``, ``rho_derivative`` and ``theta_derivative`` must be sequences of integers with the same length.

    The :math:`\rho` and :math:`\theta` values are the same for all the polynomials.
    The output is a list of numpy arrays, each containing the values of the Zernike polynomial for the corresponding order and degree.
    The list has the same length as the input sequences and the arrays have the same shape as ``rho``.

    .. note::

        If the input ``rho`` or ``theta`` are not floating point numpy arrays, it is converted to one with ``numpy.float64`` dtype.
        If the input ``rho`` or ``theta`` are floating point numpy arrays (ex: ``numpy.float32``), the computation will be done in ``numpy.float32``.
        If the input ``rho`` and ``theta`` are not of the same dtype, they are both converted to ``numpy.float64``.

    Parameters
    ----------
    rho : numpy.ndarray (N-D array)
        The radial coordinate values with shape (...,).

    theta : numpy.ndarray (N-D array)
        The angular coordinate values with shape (...,). Same shape as ``rho``.

    n : Sequence[Integral]
        A list of the radial order(s) of the Zernike polynomial(s) to compute.

    m : Sequence[Integral]
        A list of the radial degree(s) of the Zernike polynomial(s) to compute.

    rho_derivative : Optional[Sequence[Integral]], optional
        A list of the order(s) of the radial derivative(s) to compute.
        If None, is it assumed that rho_derivative is 0 for all polynomials.

    theta_derivative : Optional[Union[Integral, Sequence[Integral]]], optional
        A list of the order(s) of the angular derivative(s) to compute, expected to have shape=(Npolynomials,).
        If None, is it assumed that theta_derivative is 0 for all polynomials.

    default : Real, optional
        The default value for invalid rho values. The default is numpy.nan.
        If the radial coordinate values are not in the valid domain (0 <= rho <= 1) or if they are numpy.nan, the output is set to this value.

    precompute : bool, optional
        If True, precomputes the useful terms for better performance when computing multiple polynomials with the same rho values.
        If False, computes the useful terms on the fly for each polynomial to avoid memory overhead.
        The default is True.

    _skip : bool, optional
        If True, the checks for the input parameters are skipped. This is useful for internal use where the checks are already done.
        The default is False.

    Returns
    -------
    List[numpy.ndarray]
        A list of numpy arrays containing the Zernike polynomial values for each order and degree.
        Each array has the same shape as ``rho``.

    Raises
    ------
    TypeError
        If the rho or theta values can not be converted to a numpy array of floating points values.
        If n, m, rho_derivative or theta_derivative (if not None) are not sequences of integers.

    ValueError
        If the rho and theta do not have the same shape.
        If the lengths of n, m, rho_derivative and theta_derivative (if not None) are not the same.

    Examples
    --------
    Compute the Zernike polynomial :math:`Z_{2}^{0}(\rho, \theta)` for :math:`\rho \leq 1`:

    .. code-block:: python

        import numpy
        from pyzernike import zernike_polynomial
        rho = numpy.linspace(0, 1, 100)
        theta = numpy.linspace(0, 2*numpy.pi, 100)
        result = zernike_polynomial(rho, theta, n=[2], m=[0])
        polynomial = result[0]  # result is a list, we take the first element

    Compute the radial Zernike polynomial :math:`Z_{2}^{0}(\rho, \theta)` and its first derivative for :math:`\rho \leq 1`:

    .. code-block:: python

        import numpy
        from pyzernike import zernike_polynomial
        rho = numpy.linspace(0, 1, 100)
        theta = numpy.linspace(0, 2*numpy.pi, 100)
        result = zernike_polynomial(rho, theta, n=[2,2], m=[0,0], rho_derivative=[0, 1])
        polynomial = result[0]  # result is a list, we take the first element
        derivative = result[1]  # result is a list, we take the second element

    """
    if not _skip:
        # Convert rho and theta to numpy arrays of floating point values
        if not isinstance(rho, numpy.ndarray):
            rho = numpy.asarray(rho, dtype=numpy.float64)
        if not isinstance(theta, numpy.ndarray):
            theta = numpy.asarray(theta, dtype=numpy.float64)
        # Convert rho and theta in arrays of floating point values if they are not already
        if not numpy.issubdtype(rho.dtype, numpy.floating):
            rho = rho.astype(numpy.float64)
        if not numpy.issubdtype(theta.dtype, numpy.floating):
            theta = theta.astype(numpy.float64)
        # If rho and theta are not of the same dtype, convert them to float64
        if rho.dtype != theta.dtype:
            theta = theta.astype(numpy.float64)
            rho = rho.astype(numpy.float64)

        if not isinstance(n, Sequence) or not all(isinstance(i, Integral) for i in n):
            raise TypeError("n must be a sequence of integers.")
        if not isinstance(m, Sequence) or not all(isinstance(i, Integral) for i in m):
            raise TypeError("m must be a sequence of integers.")
        if rho_derivative is not None:
            if not isinstance(rho_derivative, Sequence) or not all(isinstance(i, Integral) and i >= 0 for i in rho_derivative):
                raise TypeError("rho_derivative must be a sequence of non-negative integers.")
        if theta_derivative is not None:
            if not isinstance(theta_derivative, Sequence) or not all(isinstance(i, Integral) and i >= 0 for i in theta_derivative):
                raise TypeError("theta_derivative must be a sequence of non-negative integers.")
        if not isinstance(default, Real):
            raise TypeError("Default value must be a real number.")
        if not isinstance(precompute, bool):
            raise TypeError("precompute must be a boolean.")
        
        if not rho.shape == theta.shape:
            raise ValueError("Rho and theta must have the same shape.")
        if len(n) != len(m):
            raise ValueError("n and m must have the same length.")
        if rho_derivative is not None and len(n) != len(rho_derivative):
            raise ValueError("n and rho_derivative must have the same length.")
        if theta_derivative is not None and len(n) != len(theta_derivative):
            raise ValueError("n and theta_derivative must have the same length.")
        if rho_derivative is None:
            rho_derivative = [0] * len(n)
        if theta_derivative is None:
            theta_derivative = [0] * len(n)

        # Compute the Mask for valid rho values
        domain_mask = (rho >= 0) & (rho <= 1)
        finite_mask = numpy.isfinite(rho) & numpy.isfinite(theta)
        valid_mask = domain_mask & finite_mask

        # Conserve only the valid values and save the input shape
        original_shape = rho.shape
        rho = rho[valid_mask]
        theta = theta[valid_mask]

    # Compute the polynomials using the core_polynomial function
    zernike_polynomials = core_polynomial(
        rho=rho,
        theta=theta,
        n=n,
        m=m,
        rho_derivative=rho_derivative,
        theta_derivative=theta_derivative,
        flag_radial=False,
        precompute=precompute
    )

    # If rho is not in the valid domain, set the output to the default value
    if not _skip:
        for index in range(len(zernike_polynomials)):
            # Reshape the radial polynomial to the original shape of rho and set the invalid values to the default value
            output_default = numpy.full(original_shape, default, dtype=numpy.float64)
            output_default[valid_mask] = zernike_polynomials[index]
            zernike_polynomials[index] = output_default

    # Return the radial polynomials
    return zernike_polynomials
