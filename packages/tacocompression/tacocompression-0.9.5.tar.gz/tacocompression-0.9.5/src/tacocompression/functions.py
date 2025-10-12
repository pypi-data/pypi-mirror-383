import math

def cantor_pairing(x: int, y: int) -> int:
    """
    Implements the Cantor pairing function. :math:`\pi(x, y) = \frac{(x+y)(x+y+1)}{2}+x`.

    :param x: First integer.
    :param y: Second integer.
    :return: Representation.
    """
    return ((x + y) * (x + y + 1)) // 2 + y

def inverse_cantor_pairing(z: int) -> tuple[int, int]:
    """
    Reverses the Cantor pairing function.
    :param z: Representation.
    :return: Original x and y
    """
    sqrt_part = math.isqrt(8 * z + 1)
    w = (sqrt_part - 1) // 2
    t = (w * w + w) // 2
    y = z - t
    x = w - y
    return x, y

def szudzik_pairing(x: int, y: int) -> int:
    """
    Implements the Szudzik pairing function. :math:`\pi(x, y) = y^2 + x` if :math:`x<y` and :math:`x^2 + x +y` else.

    :param x: First integer.
    :param y: Second integer.
    :return: Representation.
    """
    if x < y:
        return y**2 + x
    else:
        return x**2 + x + y

def inverse_szudzik_pairing(z: int) -> tuple[int, int]:
    """
    Reverses the Szudzik pairing function.

    :param z: Representation.
    :return: Original x and y
    """
    z_sqrt = math.isqrt(z)
    if z - z_sqrt**2 < z_sqrt:
        return z - z_sqrt**2, z_sqrt
    else:
        return z_sqrt, z - z_sqrt**2 - z_sqrt

def rosenberg_strong_pairing(x: int, y: int) -> int:
    """
    Implements the Rosenberg-Strong pairing function. :math:`\pi(x, y) = \max(x,y)^2 + x - y`.

    :param x: First integer.
    :param y: Second integer.
    :return: Representation.
    """
    max_val = max(x, y)
    return max_val**2 + max_val + x - y

def inverse_rosenberg_strong_pairing(z: int) -> tuple[int, int]:
    """
    Reverses the Rosenberg-Strong pairing function.
    :param z: Representation.
    :return: Original x and y
    """
    m = math.isqrt(z)
    if z - m**2 < m:
        return z - m**2, m
    else:
        return m, m**2 + 2 * m - z


