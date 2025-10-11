import numpy                as     np
import sympy                as     sp
from   sympy                import latex
from   IPython.display      import Math, display

def DIS(obj, name="obj", evalf=False, tol=5): 
    """
    Converts vectors/numbers/matrices to LaTeX with optional simplification.

    Parameters:
        obj     : Input (SymPy or NumPy object)
        name    : Name used for display
        evalf   : If T, evaluates to decimal form before display
        rational: If T, result shown as fraction; if F, decimal
        x       : Optional. If given, sets tolerance as 1e-x (e.g., x=3 → tol=1e-3)
        tol     : Optional tolerance value (overrides x if both given)
    """

    def safe_eval_entry(x):
        try:
            return sp.sympify(x).evalf(tol)
        except (TypeError, ValueError):
            return x

    if evalf:
        if isinstance(obj, np.ndarray):
            obj = sp.Matrix(obj).applyfunc(safe_eval_entry)
        elif isinstance(obj, (sp.Matrix, list)):
            obj = sp.Matrix(obj).applyfunc(safe_eval_entry)
        elif isinstance(obj, sp.NDimArray):
            obj = obj.applyfunc(safe_eval_entry)
        else:
            obj = safe_eval_entry(obj)
    else:
        if isinstance(obj, np.ndarray):
            obj = sp.Matrix(obj)
        elif isinstance(obj, (sp.Matrix, list)):
            obj = sp.Matrix(obj)
        elif isinstance(obj, sp.NDimArray):
            obj = obj
        else:
            obj = sp.sympify(obj)

    display(Math(f"{name} = {latex(obj)}"))