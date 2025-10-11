import numpy                as     np
import sympy                as     sp
from   sympy                import latex
from   IPython.display      import Math, display
import matplotlib.pyplot    as     plt
import plotly.graph_objects as     go

def DIS_EI(A, name="Matrix", evalf=False, tol=5, return_data=False, show=True, show_which="both"):
    """
    Computes and displays the eigenvalues and eigenvectors of a matrix A with enhanced display options.

    Parameters:
        A          : Square matrix (SymPy Matrix or NumPy ndarray)
        name       : Label used for the matrix (default="Matrix")
        evalf      : If True, show decimal values (default=False)
        tol        : Tolerance for decimal rounding (default=5)
        return_data: If True, also returns eigenvalues and eigenvectors (default=False)
        show       : If True, displays the output (default=True)
        show_which : What to display ("both", "eigvals", or "eigvecs") (default="both")

    Returns (if return_data=True):
        - eigvals: List of eigenvalues
        - eigvecs: List of corresponding eigenvectors (each as a SymPy Matrix)
    """

    threshold = 10**(-10)

    def safe_eval(x):
        try:
            val = x.evalf(tol)
            if abs(val) < threshold:
                return sp.Integer(0)
            return round(float(val), tol)
        except (TypeError, ValueError):
            return x

    # Convert NumPy array to SymPy Matrix if needed
    if isinstance(A, np.ndarray):
        A = sp.Matrix(A)

    # Compute eigenvalues and eigenvectors
    eigen_data = A.eigenvects()

    # To store raw data
    eigvals = []
    eigvecs = []

    # Validate show_which parameter
    show_which = show_which.lower()
    valid_options = ["both", "eigvals", "eigvecs"]
    if show_which not in valid_options:
        raise ValueError(f"show_which must be one of {valid_options}")

    # Prepare data
    counter = 1
    for eigval, mult, vects in eigen_data:
        for i in range(mult):
            val_disp = safe_eval(eigval) if evalf else eigval
            v_disp = vects[i].applyfunc(safe_eval) if evalf else vects[i]
            eigvals.append(val_disp)
            eigvecs.append(v_disp)
            counter += 1

    # Build LaTeX string based on options
    if show_which == "both":
        latex_str = f"\\text{{Eigenvalues and Eigenvectors of }} {name}: \\\\"
        for i, (val, vec) in enumerate(zip(eigvals, eigvecs)):
            latex_str += f"\\lambda_{{{i+1}}} = {latex(val)}, \\quad v_{{{i+1}}} = {latex(vec)} \\\\"
    
    elif show_which == "eigvals":
        # Default vector display for eigenvalues only
        latex_str = f"\\text{{Eigenvalues of }} {name}: \\quad \\lambda = {latex(sp.Matrix(eigvals))}"
    
    elif show_which == "eigvecs":
        # Default matrix display for eigenvectors only
        V = sp.Matrix.hstack(*[vec for vec in eigvecs])
        latex_str = f"\\text{{Eigenvectors of }} {name}: \\quad v = {latex(V)}"

    if show:
        display(Math(latex_str))

    if return_data:
        return eigvals, eigvecs