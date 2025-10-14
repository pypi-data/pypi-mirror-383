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
from typing import Optional, Tuple, Sequence, List
from numbers import Integral, Real

from .core.core_cartesian_to_elliptic_annulus import core_cartesian_to_elliptic_annulus

def cartesian_to_elliptic_annulus(
    x: Sequence[Real],
    y: Sequence[Real],
    Rx: float = 1.0,
    Ry: float = 1.0,
    x0: float = 0.0,
    y0: float = 0.0,
    alpha: float = 0.0,
    h: float = 0.0,
    x_derivative: Optional[Sequence[Integral]] = None,
    y_derivative: Optional[Sequence[Integral]] = None,
    _skip: bool = False,
    ) -> Tuple[List[numpy.ndarray], List[numpy.ndarray]]:
    r"""
    Transform Cartesian coordinates :math:`(x, y)` to elliptic annulus domain polar coordinates :math:`(\rho_{eq}, \theta_{eq})`.

    .. seealso::

        - :func:`pyzernike.elliptic_domain_to_cartesian` to convert elliptic annulus domain polar coordinates to Cartesian coordinates.
        - :func:`pyzernike.xy_zernike_polynomial` to compute Zernike polynomials on the elliptic annulus domain.
        - :func:`pyzernike.core.core_cartesian_to_elliptic_annulus` to inspect the core implementation of the computation.
        - The page :doc:`../../mathematical_description` in the documentation for the mathematical extension of the Zernike polynomials on the elliptic domain.

    Lets consider the extended elliptic annulus domain defined by the following parameters:

    .. figure:: ../../../pyzernike/resources/elliptic_annulus_domain.png
        :width: 400px
        :align: center

        The parameters to define the extended domain of the Zernike polynomial.

    The parameters are:

    - :math:`R_x` and :math:`R_y` are the lengths of the semi-axis of the ellipse.
    - :math:`x_0` and :math:`y_0` are the coordinates of the center of the ellipse.
    - :math:`\alpha` is the rotation angle of the ellipse in radians.
    - :math:`h=\frac{a}{R_x}=\frac{b}{R_y}` defining the inner boundary of the ellipse.

    The methods allow to compute the polar coordinates :math:`(\rho_{eq}, \theta_{eq})` and their derivatives with respect to the Cartesian coordinates :math:`(x, y)`.

    - ``x`` and ``y`` are expected to be numpy arrays of the same shape and same dtype.
    - ``x_derivative`` and ``y_derivative`` must be sequences of non-negative integers of the same length.

    The output is a tuple of two lists with lengths equal to the length of ``x_derivative`` and ``y_derivative``:

    - The first list contains the equivalent polar radius :math:`\rho_{eq}` and its derivatives with respect to the given orders.
    - The second list contains the equivalent polar angle :math:`\theta_{eq}` and its derivatives with respect to the given orders.

    .. note::

        If the input ``x`` or ``y`` are not floating point numpy arrays, it is converted to one with ``numpy.float64`` dtype.
        If the input ``x`` or ``y`` are floating point numpy arrays (ex: ``numpy.float32``), the computation will be done in ``numpy.float32``.
        If the input ``x`` and ``y`` are not of the same dtype, they are both converted to ``numpy.float64``.

    The derivatives for orders higher than 2 are computed using symbolic differentiation with sympy library (high computational cost).
    For orders 0, 1 and 2, the derivatives are computed using the analytical expressions derived from the chain rule.

    Parameters
    ----------
    x : Sequence[float]
        The x coordinates in Cartesian system with shape (...,).

    y : Sequence[float]
        The y coordinates in Cartesian system with shape (...,).

    Rx : float, optional
        The length of the semi-axis of the ellipse along x axis. Must be strictly positive.
        The default is 1.0, which corresponds to the unit circle.

    Ry : float, optional
        The length of the semi-axis of the ellipse along y axis. Must be strictly positive.
        The default is 1.0, which corresponds to the unit circle.

    x0 : float, optional
        The x coordinate of the center of the ellipse. Can be any real number.
        The default is 0.0, which corresponds to an ellipse centered at the origin.

    y0 : float, optional
        The y coordinate of the center of the ellipse. Can be any real number.
        The default is 0.0, which corresponds to an ellipse centered at the origin.

    alpha : float, optional
        The rotation angle of the ellipse in radians. Can be any real number.
        The default is 0.0, such as :math:`x` and :math:`y` axis are aligned with the ellipse axes.

    h : float, optional
        The ratio of the inner semi-axis to the outer semi-axis. Must be in the range [0, 1).
        The default is 0.0, which corresponds to a filled ellipse.

    x_derivative : Optional[Sequence[int]], optional
        The derivative order with respect to x to compute. Must be a sequence of non-negative integers.
        If None, is it assumed that x_derivative is [0].

    y_derivative : Optional[Sequence[int]], optional
        The derivative order with respect to y to compute. Must be a sequence of non-negative integers of the same length as `x_derivative`.
        If None, is it assumed that y_derivative is [0].

    Returns
    -------
    Tuple[List[numpy.ndarray], List[numpy.ndarray]]

        The polar coordinates (:math:`\rho_{eq}, \theta_{eq}`) and their derivatives with respect to the Cartesian coordinates :math:`(x, y)`.
        ``output[0][i]`` is the derivative with respect to x of order ``x_derivative[i]`` and with respect to y of order ``y_derivative[i]`` of :math:`\rho_{eq}`.
        ``output[1][i]`` is the derivative with respect to x of order ``x_derivative[i]`` and with respect to y of order ``y_derivative[i]`` of :math:`\theta_{eq}`.

        
    Examples
    --------
    Lets compute Zernike polynomial :math:`Z_2^0` on an extended circle of radius 2 centered at (1,1).

    First, we convert a grid of Cartesian coordinates to elliptic annulus polar coordinates using :func:`pyzernike.cartesian_to_elliptic_annulus`:

    .. code-block:: python

        import numpy
        from pyzernike import cartesian_to_elliptic_annulus

        # Define the elliptic annulus domain parameters
        Rx = 2.0  # Semi-axis along x
        Ry = 2.0  # Semi-axis along y
        x0 = 1.0  # Center x
        y0 = 1.0  # Center y

        # Create a grid of Cartesian coordinates
        x = np.linspace(-1, 3, 100)
        y = np.linspace(-1, 3, 100)
        X, Y = np.meshgrid(x, y)

        # Convert to elliptic annulus polar coordinates
        list_rho_eq, list_theta_eq = cartesian_to_elliptic_annulus(X, Y, Rx, Ry, x0, y0)

        # Extract the polar coordinates (0th order derivatives)
        rho_eq = list_rho_eq[0]
        theta_eq = list_theta_eq[0]

    Then the variables ``rho_eq`` and ``theta_eq`` can be directly used to compute Zernike polynomials on the elliptic annulus domain using :func:`pyzernike.zernike_polynomial`.
    Note that the complete process can be done in one step using :func:`pyzernike.xy_zernike_polynomial`.

    .. code-block:: python

        from pyzernike import zernike_polynomial

        # Compute the Zernike polynomial Z_2^0 on the elliptic annulus domain
        Z20 = zernike_polynomial(rho_eq, theta_eq, n=2, m=0)[0]

    If you also want to extract ``rho_eq`` and ``theta_eq``  and their first derivatives with respect to x and y, you can specify the derivative orders:

    .. code-block:: python

        # Define the derivative orders
        x_derivative = [0, 1, 0]  # 0th and 1st derivative with respect to x
        y_derivative = [0, 0, 1]  # 0th and 1st derivative with respect to y

        # Convert to elliptic annulus polar coordinates and compute derivatives
        list_rho_eq, list_theta_eq = cartesian_to_elliptic_annulus(X, Y, Rx, Ry, x0, y0, x_derivative=x_derivative, y_derivative=y_derivative)

        # Extract the polar coordinates and their derivatives
        rho_eq = list_rho_eq[0]          # 0th order derivative of rho_eq
        drho_eq_dx = list_rho_eq[1]      # 1st order derivative of rho_eq with respect to x
        drho_eq_dy = list_rho_eq[2]      # 1st order derivative of rho_eq with respect to y

        theta_eq = list_theta_eq[0]      # 0th order derivative of theta_eq
        dtheta_eq_dx = list_theta_eq[1]  # 1st order derivative of theta_eq with respect to x
        dtheta_eq_dy = list_theta_eq[2]  # 1st order derivative of theta_eq with respect to y

    These derivatives can be useful for computing gradients or Jacobians of Zernike polynomials on the elliptic annulus domain, see :func:`pyzernike.xy_zernike_polynomial` for more details.

    """
    if not _skip:
        # Convert x and y to numpy arrays of floating point values
        if not isinstance(x, numpy.ndarray):
            x = numpy.asarray(x, dtype=numpy.float64)
        if not isinstance(y, numpy.ndarray):
            y = numpy.asarray(y, dtype=numpy.float64)
        # Convert x and y in arrays of floating point values if they are not already
        if not numpy.issubdtype(x.dtype, numpy.floating):
            x = x.astype(numpy.float64)
        if not numpy.issubdtype(y.dtype, numpy.floating):
            y = y.astype(numpy.float64)
        # If x and y are not of the same dtype, convert them to float64
        if x.dtype != y.dtype:
            y = y.astype(numpy.float64)
            x = x.astype(numpy.float64)

        if x_derivative is not None:
            if not isinstance(x_derivative, Sequence) or not all(isinstance(i, Integral) and i >= 0 for i in x_derivative):
                raise TypeError("x_derivative must be a sequence of non-negative integers.")
        if y_derivative is not None:
            if not isinstance(y_derivative, Sequence) or not all(isinstance(i, Integral) and i >= 0 for i in y_derivative):
                raise TypeError("y_derivative must be a sequence of non-negative integers.")
        
        if not x.shape == y.shape:
            raise ValueError("x and y must have the same shape.")

        if not isinstance(Rx, Real) or Rx <= 0:
            raise TypeError("Rx must be a positive real number.")
        if not isinstance(Ry, Real) or Ry <= 0:
            raise TypeError("Ry must be a positive real number.")
        if not isinstance(x0, Real):
            raise TypeError("x0 must be a real number.")
        if not isinstance(y0, Real):
            raise TypeError("y0 must be a real number.")
        if not isinstance(alpha, Real):
            raise TypeError("Alpha must be a real number.")
        if not isinstance(h, Real) or not (0 <= h < 1):
            raise TypeError("h must be a real number in the range [0, 1[.")

        if x_derivative is None and y_derivative is None:
            x_derivative = [0]
            y_derivative = [0]
        elif x_derivative is None and y_derivative is not None:
            x_derivative = [0] * len(y_derivative)
        elif x_derivative is not None and y_derivative is None:
            y_derivative = [0] * len(x_derivative)
        if len(x_derivative) != len(y_derivative):
            raise ValueError("x_derivative and y_derivative must have the same length.")
        
    return core_cartesian_to_elliptic_annulus(x, y, Rx, Ry, x0, y0, alpha, h, x_derivative, y_derivative)