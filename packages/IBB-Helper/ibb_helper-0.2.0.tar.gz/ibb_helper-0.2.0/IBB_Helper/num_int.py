def num_int(expr, x_sym=None, x_range=None, n_pts=400):
    """
    Numerically integrate a symbolic expression, list, or matrix over a 1D domain
    and convert the result to a SymPy object.

    Parameters
    ----------
    expr : sympy expression, list, or sympy.Matrix
        Expression(s) to integrate
    x_sym : sympy.Symbol
        Independent variable
    x_range : tuple(float, float)
        Integration limits (x_start, x_end)
    n_pts : int
        Number of quadrature points

    Returns
    -------
    sympy.Float or sympy.Matrix
        Numeric integral converted to SymPy
    """
    import numpy as np
    from sympy import lambdify, Matrix, Float, latex, sympify
    from IPython.display import display, Math

    x_start, x_end = x_range
    x_vals = np.linspace(x_start, x_end, n_pts)
    dx = x_vals[1] - x_vals[0]

    # Convert lists to Matrix for uniform handling
    if isinstance(expr, list):
        expr = Matrix(expr)

    # Scalar expression
    if not isinstance(expr, Matrix):
        f = lambdify(x_sym, expr, 'numpy')
        result = Float(np.sum(f(x_vals) * dx))

    # Matrix expression
    else:
        rows, cols = expr.shape
        result = Matrix.zeros(rows, cols)
        for i in range(rows):
            for j in range(cols):
                f = lambdify(x_sym, expr[i, j], 'numpy')
                result[i, j] = Float(np.sum(f(x_vals) * dx))

    return result
