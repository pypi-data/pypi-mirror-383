import numpy                as     np
import sympy                as     sp
from   sympy                import latex
from   IPython.display      import Math, display
import matplotlib.pyplot    as     plt
import plotly.graph_objects as     go

def DMAT(matrix, name="Matrix", r=5, c=5, evalf=False, tol=5):
    """
    Displays a truncated matrix with optional numerical evaluation and rational simplification.
    
    Parameters:
        matrix  : Input matrix (NumPy array, SymPy Matrix, or list)
        name    : Display name (default: "Matrix")
        r       : Max rows to display (default: 5)
        c       : Max columns to display (default: 5)
        evalf   : If T, apply numerical evaluation (default: F)
        rational: If T, display as fraction; else as decimal (default: T)
        x       : Optional. If given, sets tolerance as 1e-x
        tol     : Optional tolerance value (overrides x if both are given)
    """
    
    # Convert to SymPy Matrix if needed
    if isinstance(matrix, (np.ndarray, list)):
        matrix = sp.Matrix(matrix)

    # Truncate to r rows and c columns
    submatrix = matrix[:min(r, matrix.rows), :min(c, matrix.cols)]

    # Apply evaluation if needed
    if evalf:
        processed = submatrix.applyfunc(lambda x: x.evalf(tol))
    else:
        processed = submatrix

    # Display matrix
    display(Math(f"{name} = {latex(processed)}"))

    m = matrix.rows
    n = matrix.cols
    # Show truncation message if applicable
    if matrix.rows > r or matrix.cols > c:
        display(Math(rf"\text{{... Truncated to first {r}x{c} out of {m}x{n} matrix}}"))