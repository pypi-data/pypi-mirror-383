"""
Provides quick access to some useful transformations expressed as PostScript matrices
"""

def identity() -> tuple[float, float, float, float, float, float]:
    """
    Returns an identity matrix as a 6 element tuple.
    """
    ...

def compose(
    mat1: tuple[float, float, float, float, float, float],
    mat2: tuple[float, float, float, float, float, float],
) -> tuple[float, float, float, float, float, float]:
    """
    Returns a matrix which is the composition of the two input transformations.
    """
    ...

def inverse(
    mat: tuple[float, float, float, float, float, float],
) -> tuple[float, float, float, float, float, float]:
    """
    Returns a matrix which is the inverse of the input transformation.
    (Note: There will not always be an inverse)
    """
    ...

def rotate(theta: float) -> tuple[float, float, float, float, float, float]:
    """
    Returns a matrix which will rotate by `theta`. `theta` is expressed in radians.
    """
    ...

def scale(
    x: float, y: float | None = None
) -> tuple[float, float, float, float, float, float]:
    """
    Returns a matrix which will scale by `x` in the horizontal direction and
    `y` in the vertical. If `y` is omitted, it will scale by the same
    amount (`x`) in both directions.
    """
    ...

def skew(theta: float) -> tuple[float, float, float, float, float, float]:
    """
    Returns a matrix which will skew by `theta` (to produce an oblique font).
    `theta` is expressed in radians.
    """
    ...

def translate(x: float, y: float) -> tuple[float, float, float, float, float, float]:
    """
    Returns a matrix which will translate by `x` in the horizontal direction
    and `y` in the vertical.
    """
    ...
