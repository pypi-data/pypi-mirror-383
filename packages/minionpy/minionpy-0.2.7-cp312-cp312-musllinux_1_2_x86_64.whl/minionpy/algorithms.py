import sys
import os 
import ctypes
from functools import wraps

current_file_directory = os.path.dirname(os.path.abspath(__file__))
custom_path = os.path.join(current_file_directory, 'lib')
sys.path.append(custom_path)

import numpy as np
from minionpycpp import LSHADE as cppLSHADE
from minionpycpp import LSHADE as cppJADE
from minionpycpp import ARRDE as cppARRDE
from minionpycpp import NLSHADE_RSP as cppNLSHADE_RSP
from minionpycpp import j2020 as cppj2020
from minionpycpp import jSO as cppjSO
from minionpycpp import LSRTDE as cppLSRTDE
from minionpycpp import Differential_Evolution as cppDifferential_Evolution
from minionpycpp import GWO_DE as cppGWO_DE
from minionpycpp import Minimizer as cppMinimizer
from minionpycpp import NelderMead as cppNelderMead 
from minionpycpp import ABC as cppABC
from minionpycpp import Dual_Annealing as cppDual_Annealing
from minionpycpp import L_BFGS_B as cppL_BFGS_B
from minionpycpp import L_BFGS as cppL_BFGS
from minionpycpp import PSO as cppPSO
from minionpycpp import SPSO2011 as cppSPSO2011
from minionpycpp import DMSPSO as cppDMSPSO
from minionpycpp import LSHADE_cnEpSin as cppLSHADE_cnEpSin
from minionpycpp import CMAES as cppCMAES
from minionpycpp import BIPOP_aCMAES as cppBIPOP_aCMAES



_PyGILState_Ensure = ctypes.pythonapi.PyGILState_Ensure
_PyGILState_Ensure.restype = ctypes.c_void_p
_PyGILState_Ensure.argtypes = []

_PyGILState_Release = ctypes.pythonapi.PyGILState_Release
_PyGILState_Release.restype = None
_PyGILState_Release.argtypes = [ctypes.c_void_p]


def _gil_protected(func):
    """Wrap a callable so it always executes with the Python GIL held."""
    if func is None:
        return None

    @wraps(func)
    def wrapper(*args, **kwargs):
        state = _PyGILState_Ensure()
        try:
            return func(*args, **kwargs)
        finally:
            _PyGILState_Release(state)

    return wrapper


from typing import Callable, Dict, List, Optional, Any
  
class MinionResult:
    """
    Stores the results of an optimization process.

    This class encapsulates key optimization metrics, including:

    - **x** (*list*): Best solution found.
    - **fun** (*float*): Objective function value at `x`.
    - **nit** (*int*): Number of iterations performed.
    - **nfev** (*int*): Number of function evaluations.
    - **success** (*bool*): Whether the optimization was successful.
    - **message** (*str*): Descriptive message about the optimization outcome.

    Notes
    -----
    The structure of `MinionResult` closely resembles `scipy.optimize.OptimizeResult`,
    making it easy to use in similar contexts.
    """

    def __init__(self, minRes):
        """
        Initialize a `MinionResult` instance from a C++ optimization result.

        Parameters
        ----------
        minRes : C++ MinionResult object
            The optimization result returned by the C++ optimization engine.
        """
        self.x = minRes.x
        self.fun = minRes.fun
        self.nit = minRes.nit
        self.nfev = minRes.nfev
        self.success = minRes.success
        self.message = minRes.message
        self.result = minRes

    def __repr__(self):
        """
        Return a string representation of the `MinionResult` object.

        Returns
        -------
        str
            A formatted string displaying key optimization results.
        """
        return (f"MinionResult(x={self.x}, fun={self.fun}, nit={self.nit}, "
                f"nfev={self.nfev}, success={self.success}, message={self.message})")

    
class CalllbackWrapper: 
    """
    Wraps a Python function that takes cppMinionResult as an argument to work with MinionResult.
    
    Converts a callback function from working with cppMinionResult to MinionResult.
    """

    def __init__(self, callback):
        """
        Initialize CallbackWrapper.

        Parameters:
        - callback: A function that takes cppMinionResult as an argument.
        """
        self.callback = callback

    def __call__(self, minRes):
        """
        Invoke the callback function with a MinionResult object.

        Parameters:
        - minRes: MinionResult object to pass to the callback function.

        Returns:
        - Result of the callback function.
        """
        minionResult = MinionResult(minRes)
        return self.callback(minionResult)
    

class MinimizerBase:
    """
    Base class for minimization algorithms.

    This class performs initial validation and preprocessing of input parameters
    before passing them to the chosen optimization algorithm.
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None) : 
        """
        Initialize the `MinimizerBase` class.

        Parameters
        ----------
        func : callable
            Objective function to be minimized. Must accept list[list[float]]. If the function operates on a single sample, it should be vectorized.
        bounds : list of tuple
            List of `(lower, upper)` bounds for each decision variable.
        x0 : list[list[float]], optional
            Initial guesses for the solution. Note that Minion assumes multiple initial guesses, thus, x0 is a list[list[float]] object. These guesses will be used for population initialization.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops when the relative improvement falls below this value. 
            Default is `1e-4`.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is `100000`.
        callback : callable, optional
            A function that is called at each iteration. It must accept the current optimization state as an argument.
        seed : int, optional
            Random seed for reproducibility. If `None`, a random seed is used.
        options : dict, optional
            Additional algorithm-specific parameters. If `None`, default settings are used.

        Raises
        ------
        TypeError
            If any of the input parameters are of an incorrect type.
        ValueError
            If `x0` has a different length than `bounds`, or if bounds are not properly formatted.
        """

        if not callable(func):
            raise TypeError("func must be callable")
        if not isinstance(bounds, list) or not all(isinstance(b, tuple) and len(b) == 2 for b in bounds):
            raise TypeError("bounds must be a list of tuples (float, float)")
        #if x0 is not None and not all(isinstance(x, list) for x in x0):
        #    raise TypeError("x0 must be a list of list of floats or None")
        if not isinstance(relTol, float):
            raise TypeError("relTol must be a float")
        if not isinstance(maxevals, int):
            raise TypeError("maxevals must be an int")
        if callback is not None and not callable(callback):
            raise TypeError("callback must be callable or None")
        if seed is not None and not isinstance(seed, int):
            raise TypeError("seed must be an int or None")
        if options is not None :
            if not isinstance(options, dict): raise TypeError("options must be None or a dictionary")

        self.pyfunc = func 
        self.bounds = self._validate_bounds(bounds)
        self.x0 = x0 
        if self.x0 is not None : 
            if isinstance(self.x0, list) :
                for x in x0 :
                    if len(x) != len(self.bounds) : 
                        raise ValueError("Initial guesses must have the same dimension as the length of the bounds.")
            else : 
                raise TypeError("Initial guesses x0 must have type list[list[float]]")   
            
        self.x0cpp = self.x0 if self.x0 is not None else []
        self.data = None

        self.callback = callback  
        self.cppCallback = CalllbackWrapper(self.callback) if callback is not None else None

        # The C++ backend now releases the GIL around the main optimization loop.
        # Wrap the objective and callback so they always reacquire the GIL when invoked.
        self._func_for_cpp = _gil_protected(self.func)
        self._callback_for_cpp = _gil_protected(self.cppCallback) if self.cppCallback is not None else None

        self.relTol = relTol
        self.maxevals = maxevals
        self.seed = seed if seed is not None else -1
        self.history = []
        self.minionResult = None
        self.options= options if options is not None else {}

    def func(self, xmat, data) : 
        """
        Transform the user-defined objective function into a compatible form for Minion.

        Parameters
        ----------
        xmat : list[list[float]] 
            Input matrix where each row is a decision variable vector.
        data : object
            Additional data (unused in this implementation).

        Returns
        -------
        list
            Function evaluation results for each row in `xmat`.
        """
        return self.pyfunc(xmat) 

    def _validate_bounds(self, bounds):
        """
        Validate the format of the decision variable bounds.

        Parameters
        ----------
        bounds : list of tuple
            List of `(lower_bound, upper_bound)` tuples.

        Returns
        -------
        list of tuple
            Validated bounds as a list of `(lower, upper)` pairs.

        Raises
        ------
        ValueError
            If bounds are improperly formatted or contain invalid values.
        """
        try:
            bounds = np.array(bounds)
        except:
            raise ValueError("Invalid bounds.")
        if np.any(bounds[:, 0]>= bounds[:,1]): raise ValueError ("upper bound must be larger than lower bound.")
        if bounds.shape[1] != 2:
            raise ValueError("Invalid bounds. Bounds must be a list of (lower_bound, upper_bound).")
        return [(b[0], b[1]) for b in bounds]

class GWO_DE(MinimizerBase):
    """
    Implementation of the Grey Wolf Optimizer with Differential Evolution (GWO-DE) algorithm.

    This class inherits from `MinimizerBase` and implements the GWO-DE optimization algorithm.
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the Grey Wolf Optimizer with Differential Evolution (GWO-DE).

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats. Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 :  list[list[float]], optional
            Initial guesses for the solution. These guesses will be used to initialize the population. 
            If None (default), a random initialization within the given bounds is used.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for the algorithm. If None (default), the following 
            settings are used::

                options = {
                    "population_size": 0,        # Determines population size dynamically
                    "mutation_rate": 0.5,        # Probability of mutation
                    "crossover_rate": 0.7,       # Probability of crossover
                    "elimination_prob": 0.1,     # Probability of elimination
                    "bound_strategy": "reflect-random"  # Boundary handling strategy
                }

            The available options are:

            - **population_size** (int):  Initial population size. If set to `0`, it will be automatically determined.
            - **mutation_rate** (float):  Mutation rate variable (F).
            - **crossover_rate** (float):  Crossover probability/rate (CR).
            - **elimination_prob** (float):  Elimination probability.
            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppGWO_DE`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """
        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppGWO_DE(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the GWO-DE optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs Nelder-Mead optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult

class NelderMead(MinimizerBase):
    """
    Implementation of the Nelder-Mead algorithm.

    This class inherits from `MinimizerBase`.
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the Nelder-Mead algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 :  list[list[float]], optional
            Initial guesses for the solution. These guesses will be used to initialize the population. 
            If None (default), a random initialization within the given bounds is used.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "bound_strategy"          : "reflect-random"
                }

            The available options are:

            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppNelderMead`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        if x0 is None : 
            raise Exception("Initial guesses x0 must not be none nor empty for Nelder-Mead to work!")
        self.optimizer = cppNelderMead(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)

    def optimize(self):
        """
        Run the Nelder-Mead optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs Nelder-Mead optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult



class PSO(MinimizerBase):
    r"""
    Canonical particle swarm optimization (global-best topology).

    Options
    -------
    The `options` dictionary accepts:

    - ``population_size`` (*int*): swarm size (defaults to ``5 * D`` when 0).
    - ``inertia_weight`` (*float*): inertia term :math:`\omega` (default ``0.7``).
    - ``cognitive_coefficient`` (*float*): self-attraction coefficient :math:`c_1`.
    - ``social_coefficient`` (*float*): global-attraction coefficient :math:`c_2`.
    - ``velocity_clamp`` (*float*): fraction of the search range used as velocity limit.
    - ``use_latin`` (*bool*): initialize swarm with Latin hypercube sampling if ``True``.
    - ``support_tolerance`` (*bool*): enable the diversity based stop criterion.
    - ``bound_strategy`` (*str*): boundary handling policy (``"reflect-random"`` by default).
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None) -> None:
        r"""
        Initialize the PSO algorithm.

        Parameters
        ----------
        func : callable
            Objective function to minimise. The function must accept a list of
            candidate solutions and return a list of objective values.
        bounds : list of tuple
            Search-space bounds expressed as ``(lower, upper)`` pairs.
        x0 : list[list[float]], optional
            Optional particle positions used to seed the swarm.  When ``None``
            (default) the swarm is initialised within the supplied bounds.
        relTol : float, optional
            Relative tolerance used by the diversity-based stopping criterion.
            Default is ``1e-4``.
        maxevals : int, optional
            Maximum number of objective evaluations allowed. Default ``100000``.
        callback : callable, optional
            Callable invoked after each iteration with the current
            :class:`MinionResult`.  Default ``None``.
        seed : int, optional
            Random seed for reproducibility.  If ``None`` (default) a random seed
            is chosen.
        options : dict, optional
            Configuration dictionary.  If ``None`` the following defaults are used::

                {
                    "population_size"       : 0,
                    "inertia_weight"        : 0.7,
                    "cognitive_coefficient" : 1.5,
                    "social_coefficient"    : 1.5,
                    "velocity_clamp"        : 0.2,
                    "bound_strategy"        : "reflect-random"
                }

            The available options are:

            - **population_size** (*int*): Swarm size (``0`` → ``5 * D``).
            - **inertia_weight** (*float*): Inertia weight :math:`\omega`.
            - **cognitive_coefficient**, **social_coefficient** (*float*): Accelerations :math:`c_1`, :math:`c_2`.
            - **velocity_clamp** (*float*): Fraction of the search range used as the velocity limit (``0`` disables).
            - **bound_strategy** (*str*): Boundary handling policy.
        """
        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppPSO(
            self._func_for_cpp,
            self.bounds,
            self.x0cpp,
            self.data,
            self._callback_for_cpp,
            relTol,
            maxevals,
            self.seed,
            self.options,
        )

    def optimize(self) -> MinionResult:
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.diversity = list(getattr(self.optimizer, "diversity", []))
        self.spatialDiversity = list(getattr(self.optimizer, "spatialDiversity", []))
        return self.minionResult


class SPSO2011(MinimizerBase):
    """
    Stochastic PSO 2011 (Clerc/Bratton) with constriction and adaptive neighbourhoods.

    Options
    -------
    Default options used when ``options`` is ``None``::

        {
            "population_size"       : 0,
            "inertia_weight"        : 0.729844,
            "cognitive_coefficient" : 1.49618,
            "social_coefficient"    : 1.49618,
            "phi_personal"          : 1.49618,
            "phi_social"            : 1.49618,
            "neighborhood_size"     : 3,
            "informant_degree"      : 3,
            "velocity_clamp"        : 0.0,
            "normalize"             : False,
            "bound_strategy"        : "reflect-random"
        }

    - ``population_size`` (*int*): swarm size (``0`` → ``5 * D``).
    - ``inertia_weight`` (*float*), ``cognitive_coefficient`` (*float*), ``social_coefficient`` (*float*): PSO constants.
    - ``informant_degree`` / ``neighborhood_size`` (*int*): number of informants per particle.
    - ``velocity_clamp`` (*float*): optional velocity clamp fraction.
    - ``normalize`` (*bool*): operate in normalised coordinates before mapping back to the original bounds.
    - ``bound_strategy`` (*str*): boundary handling policy.
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None) -> None:
        """
        Initialize the SPSO2011 algorithm.

        Parameters
        ----------
        func : callable
            Objective function to be minimised (vectorised, see :class:`PSO`).
        bounds : list of tuple
            Search-space bounds for each variable.
        x0, relTol, maxevals, callback, seed, options :
            Same semantics as :class:`PSO`.

        """
        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppSPSO2011(
            self._func_for_cpp,
            self.bounds,
            self.x0cpp,
            self.data,
            self._callback_for_cpp,
            relTol,
            maxevals,
            self.seed,
            self.options,
        )

    def optimize(self) -> MinionResult:
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.diversity = list(getattr(self.optimizer, "diversity", []))
        self.spatialDiversity = list(getattr(self.optimizer, "spatialDiversity", []))
        return self.minionResult


class DMSPSO(MinimizerBase):
    """
    Dynamic multi-swarm PSO with periodic regrouping and co-operative subswarms.

    Options
    -------
    - ``population_size`` (*int*): swarm size (defaults to ``5 * D`` when 0).
    - ``inertia_weight`` (*float*), ``cognitive_coefficient`` (*float*), ``social_coefficient`` (*float*): base PSO coefficients.
    - ``local_coefficient`` (*float*): influence of the subswarm best (default ``1.4``).
    - ``global_coefficient`` (*float*): influence of the global best (default ``0.8``).
    - ``subswarm_count`` (*int*): number of dynamic subswarms (default ``4``).
    - ``regroup_period`` (*int*): iterations between subswarm reshuffles (default ``5``).
    - ``velocity_clamp`` (*float*): fraction of the search range used as the velocity limit (default ``0.2``).
    - ``bound_strategy`` (*str*): boundary handling policy (``"reflect-random"`` by default).
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None) -> None:
        """
        Initialize the DMS-PSO algorithm.

        Parameters
        ----------
        func, bounds, x0, relTol, maxevals, callback, seed, options :
            See :class:`PSO` for the base semantics.

        Notes
        -----
        Additional entries recognised in ``options``:

        - **local_coefficient** (*float*): Weight applied to the sub-swarm best
          (default ``1.4``).
        - **global_coefficient** (*float*): Weight applied to the global best
          (default ``0.8``).
        - **subswarm_count** (*int*): Number of concurrent sub-swarms.
        - **regroup_period** (*int*): Iterations between sub-swarm reshuffles.
        """
        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppDMSPSO(
            self._func_for_cpp,
            self.bounds,
            self.x0cpp,
            self.data,
            self._callback_for_cpp,
            relTol,
            maxevals,
            self.seed,
            self.options,
        )

    def optimize(self) -> MinionResult:
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.diversity = list(getattr(self.optimizer, "diversity", []))
        self.spatialDiversity = list(getattr(self.optimizer, "spatialDiversity", []))
        return self.minionResult



class LSHADE(MinimizerBase):
    """
    Implementation of the Linear Population Reduction - Success History Adaptive Differential Evolution (LSHADE) algorithm.

    Reference : R. Tanabe and A. S. Fukunaga, "Improving the search performance of SHADE using linear population size reduction," 2014 IEEE Congress on Evolutionary Computation (CEC), Beijing, China, 2014, pp. 1658-1665, doi: 10.1109/CEC.2014.6900380.

    This class inherits from `MinimizerBase`.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the LSHADE algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 :  list[list[float]], optional
            Initial guesses for the solution. These guesses will be used to initialize the population. 
            If None (default), a random initialization within the given bounds is used.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "population_size"         :  0,  
                    "memory_size"             :  6, 
                    "mutation_strategy"       : "current_to_pbest_A_1bin",
                    "archive_size_ratio"      :  2.6, 
                    "minimum_population_size" :  4, 
                    "reduction_strategy"      : "linear",
                    "bound_strategy"          : "reflect-random"
                }

            The available options are:

            - **population_size** (int):  Initial population size (N). If set to `0`, it will be automatically determined. 
                .. math::

                        N = 5 \\cdot D

                where *D* is the dimensionality of the problem.
            - **memory_size** (int):  Number of entries in memory to store successful crossover (CR) and mutation (F) parameters.
            - **mutation_strategy** (str):  Mutation strategy used in the optimization process. Available strategies:  
                    ``"best1bin"``, ``"best1exp"``, ``"rand1bin"``, ``"rand1exp"``,  
                    ``"current_to_pbest1bin"``, ``"current_to_pbest1exp"``,  
                    ``"current_to_pbest_A_1bin"``, ``"current_to_pbest_A_1exp"``.
            - **archive_size_ratio** (float): Ratio of the archive size to the current population size.
            - **minimum_population_size** (int): Final population size after reduction.
            - **reduction_strategy** (str):  Strategy used to reduce the population size. Available strategies:  
                    ``"linear"``, ``"exponential"``, ``"agsk"``.
            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppLSHADE`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppLSHADE(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.meanCR = self.optimizer.meanCR
        self.meanF = self.optimizer.meanF
        self.stdCR = self.optimizer.stdCR
        self.stdF = self.optimizer.stdF
        self.diversity = self.optimizer.diversity
        return self.minionResult


class LSHADE_cnEpSin(MinimizerBase):
    """
    Ensemble sinusoidal LSHADE with covariance learning (cnEpSin variant).

    Reference
    ---------
    N. H. Awad, M. Z. Ali and P. N. Suganthan, "Ensemble Sinusoidal Differential
    Covariance Matrix Adaptation with Euclidean Neighborhood for Solving CEC2017
    Benchmark Problems," IEEE CEC 2017.
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None) -> None:
        """
        Initialize the LSHADE-cnEpSin algorithm.

        Parameters
        ----------
        func : callable
            Vectorised objective function returning a list of objective values.
        bounds : list of tuple
            Bounds for each decision variable.
        x0 : list[list[float]], optional
            Optional initial population.  When ``None`` the population is drawn
            uniformly within the supplied bounds.
        relTol, maxevals, callback, seed :
            Same semantics as :class:`LSHADE`.
        options : dict, optional
            Additional configuration.  If ``None`` the following defaults are
            applied::

                options = {
                    "population_size"        :   0,
                    "memory_size"            :   5,
                    "archive_rate"           :   1.4,
                    "minimum_population_size":   4,
                    "p_best_fraction"        :   0.11,
                    "rotation_probability"   :   0.4,
                    "neighborhood_fraction"  :   0.5,
                    "freq_init"              :   0.5,
                    "learning_period"        :  20,
                    "sin_freq_base"          :   0.5,
                    "epsilon"                : 1e-8,
                    "bound_strategy"         : "reflect-random"
                }
        """
        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppLSHADE_cnEpSin(
            self._func_for_cpp,
            self.bounds,
            self.x0cpp,
            self.data,
            self._callback_for_cpp,
            relTol,
            maxevals,
            self.seed,
            self.options,
        )

    def optimize(self) -> MinionResult:
        """Run LSHADE-cnEpSin and expose statistics captured by the C++ backend."""
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.meanCR = list(getattr(self.optimizer, "meanCR", []))
        self.meanF = list(getattr(self.optimizer, "meanF", []))
        self.stdCR = list(getattr(self.optimizer, "stdCR", []))
        self.stdF = list(getattr(self.optimizer, "stdF", []))
        self.diversity = list(getattr(self.optimizer, "diversity", []))
        return self.minionResult


class CMAES(MinimizerBase):
    """
    Implementation of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES).

    Reference : Hansen, N. and Ostermeier, A., "Adapting Arbitrary Normal Mutation
    Distributions in Evolution Strategies," 1996.

    This class inherits from `MinimizerBase`.
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None) -> None:
        """
        Initialize the CMA-ES algorithm.

        Parameters
        ----------
        func : callable
            Vectorised objective function returning a list of objective values.
        bounds : list of tuple
            Bounds for each decision variable.
        x0 : list[list[float]], optional
            Optional collection of initial guesses. When multiple candidates are
            supplied, the best according to ``func`` seeds the initial mean.
        relTol : float, optional
            Relative tolerance used by the stopping criterion. Default ``1e-4``.
        maxevals : int, optional
            Maximum number of function evaluations. Default ``100000``.
        callback : callable, optional
            User callback receiving intermediate :class:`MinionResult` objects.
        seed : int, optional
            Seed for the pseudo-random number generator. ``None`` keeps the
            global RNG state.
        options : dict, optional
            Additional CMA-ES configuration. If ``None`` the following defaults
            are applied::

                options = {
                    "population_size"  : 0,
                    "mu"               : 0,
                    "initial_step"     : 0.3,
                    "cc"               : 0.0,
                    "cs"               : 0.0,
                    "c1"               : 0.0,
                    "cmu"              : 0.0,
                    "damps"            : 0.0,
                    "bound_strategy"   : "reflect-random"
                }
        """
        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppCMAES(
            self._func_for_cpp,
            self.bounds,
            self.x0cpp,
            self.data,
            self._callback_for_cpp,
            relTol,
            maxevals,
            self.seed,
            self.options,
        )

    def optimize(self) -> MinionResult:
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult
    

class BIPOP_aCMAES(MinimizerBase):
    """
    Implementation of the BIPOP Adaptive Covariance Matrix Adaptation Evolution Strategy (BIPOP aCMA-ES).

    Reference : Nikolaus Hansen. 2009. Benchmarking a BI-population CMA-ES on the BBOB-2009 function testbed. In Proceedings of the 11th Annual Conference Companion on Genetic and Evolutionary Computation Conference: Late Breaking Papers (GECCO '09). Association for Computing Machinery, New York, NY, USA, 2389–2396. https://doi.org/10.1145/1570256.1570333

    This class inherits from `MinimizerBase`.
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None) -> None:
        """
        Initialize the BIPOP aCMA-ES algorithm.

        Parameters
        ----------
        func : callable
            Vectorised objective function returning a list of objective values.
        bounds : list of tuple
            Bounds for each decision variable.
        x0 : list[list[float]], optional
            Optional collection of initial guesses. When multiple candidates are
            supplied, the best according to ``func`` seeds the initial mean.
        relTol : float, optional
            Relative tolerance used by the stopping criterion. Default ``1e-4``.
        maxevals : int, optional
            Maximum number of function evaluations. Default ``100000``.
        callback : callable, optional
            User callback receiving intermediate :class:`MinionResult` objects.
        seed : int, optional
            Seed for the pseudo-random number generator. ``None`` keeps the
            global RNG state.
        options : dict, optional
            Additional CMA-ES configuration. If ``None`` the following defaults
            are applied::

                options = {
                    "population_size" : 0,    # If 0, determined automatically
                    "max_restarts"    : 8,    # Maximum number of adaptive restarts
                    "max_iterations"  : 5000, # Max iterations per run
                    "initial_step"    : 0.3,  # Initial CMA-ES step size (sigma)
                    "bound_strategy"  : "reflect-random" # Boundary handling
                }
        """
        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppBIPOP_aCMAES(
            self._func_for_cpp,
            self.bounds,
            self.x0cpp,
            self.data,
            self._callback_for_cpp,
            relTol,
            maxevals,
            self.seed,
            self.options,
        )

    def optimize(self) -> MinionResult:
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult


class jSO(MinimizerBase):
    """
    Implementation of the jSO algorithm.

    Reference : J. Brest, M. S. Maučec and B. Bošković, "Single objective real-parameter optimization: Algorithm jSO," 2017 IEEE Congress on Evolutionary Computation (CEC), Donostia, Spain, 2017, pp. 1311-1318, doi: 10.1109/CEC.2017.7969456.

    Inherits from MinimizerBase.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.


            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 :  list[list[float]], optional
            Initial guesses for the solution. These guesses will be used to initialize the population. 
            If None (default), a random initialization within the given bounds is used.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "population_size"           : 0,  
                    "memory_size"               :  5, 
                    "archive_size_ratio"        : 1.0, 
                    "minimum_population_size"   :  4, 
                    "reduction_strategy"        : "linear",
                    "bound_strategy"            : "reflect-random"
                }

            The available options are:

            - **population_size** (int): Initial population size (N). If set to `0`, it will be automatically determined as:

                .. math::

                    N = 25 \\cdot \\log(D) \\cdot \\sqrt{D}

                where *D* is the dimensionality of the problem.
            - **memory_size** (int):  Number of entries in memory to store successful crossover (CR) and mutation (F) parameters.
            - **archive_size_ratio** (float): Ratio of the archive size to the current population size.
            - **minimum_population_size** (int): Final population size after reduction.
            - **reduction_strategy** (str):  Strategy used to reduce the population size. Available strategies:  
                    ``"linear"``, ``"exponential"``, ``"agsk"``.
            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppjSO`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppjSO(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.meanCR = self.optimizer.meanCR
        self.meanF = self.optimizer.meanF
        self.stdCR = self.optimizer.stdCR
        self.stdF = self.optimizer.stdF
        self.diversity = self.optimizer.diversity
        return self.minionResult
    

class JADE(MinimizerBase):
    """
    Implementation of the JADE algorithm.

    Reference : J. Zhang and A. C. Sanderson, "JADE: Adaptive Differential Evolution With Optional External Archive," in IEEE Transactions on Evolutionary Computation, vol. 13, no. 5, pp. 945-958, Oct. 2009, doi: 10.1109/TEVC.2009.2014613.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.


            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 :  list[list[float]], optional
            Initial guesses for the solution. These guesses will be used to initialize the population. 
            If None (default), a random initialization within the given bounds is used.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "population_size"               :  0,  
                    "c"                             : 0.1, 
                    "mutation_strategy"             :  "current_to_pbest_A_1bin",
                    "archive_size_ratio"            :  1.0, 
                    "minimum_population_size"       :  4, 
                    "reduction_strategy"            : "linear",
                    "bound_strategy"                : "reflect-random"
                }

            The available options are:

            - **population_size** (int): Initial population size (N). If set to ``0``, it will be automatically determined as follows:

                - If the dimensionality :math:`D` of the problem is :math:`D < 10`, then :math:`N = 30`.
                - If :math:`10 \\leq D \\leq 30`, then :math:`N = 100`.
                - If :math:`30 < D \\leq 50`, then :math:`N = 200`.
                - If :math:`50 < D \\leq 70`, then :math:`N = 300`.
                - Else, :math:`N = 400`.

            - **c** (float) : The value of *c* variable. The value must be between 0 and 1. 
            - **mutation_strategy** (str):  Mutation strategy used in the optimization process. Available strategies:  
                    ``"best1bin"``, ``"best1exp"``, ``"rand1bin"``, ``"rand1exp"``,  
                    ``"current_to_pbest1bin"``, ``"current_to_pbest1exp"``,  
                    ``"current_to_pbest_A_1bin"``, ``"current_to_pbest_A_1exp"``.
            - **archive_size_ratio** (float): Ratio of the archive size to the current population size.
            - **minimum_population_size** (int): Final population size after reduction.
            - **reduction_strategy** (str):  Strategy used to reduce the population size. Available strategies:  
                    ``"linear"``, ``"exponential"``, ``"agsk"``.
            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppJADE`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppJADE(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.meanCR = self.optimizer.meanCR
        self.meanF = self.optimizer.meanF
        self.stdCR = self.optimizer.stdCR
        self.stdF = self.optimizer.stdF
        self.diversity = self.optimizer.diversity
        return self.minionResult
    
    
class NLSHADE_RSP(MinimizerBase):
    """
    Implementation of the LSHADE_RSP algorithm.

    Reference : V. Stanovov, S. Akhmedova and E. Semenkin, "NL-SHADE-RSP Algorithm with Adaptive Archive and Selective Pressure for CEC 2021 Numerical Optimization," 2021 IEEE Congress on Evolutionary Computation (CEC), Kraków, Poland, 2021, pp. 809-816, doi: 10.1109/CEC45853.2021.9504959.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 :  list[list[float]], optional
            Initial guesses for the solution. These guesses will be used to initialize the population. 
            If None (default), a random initialization within the given bounds is used.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "population_size"       :  0,  
                    "memory_size"           : 100,
                    "archive_size_ratio"    : 2.6 , 
                    "bound_strategy"        : "reflect-random"
                }

            The available options are:

            - **population_size** (int):  Initial population size (N). If set to `0`, it will be automatically determined. 
                .. math::

                        N = 30 \\cdot D

                where *D* is the dimensionality of the problem.
            - **memory_size** (int):  Number of entries in memory to store successful crossover (CR) and mutation (F) parameters.
            - **archive_size_ratio** (float): Ratio of the archive size to the current population size.
            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppNLSHADE_RSP`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppNLSHADE_RSP(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult
    
class ABC(MinimizerBase):
    """
    Implementation of the artifical bee colony optimization algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 :  list[list[float]], optional
            Initial guesses for the solution. These guesses will be used to initialize the population. 
            If None (default), a random initialization within the given bounds is used.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "population_size"       :  0,  
                    "mutation_strategy"     : "rand1,
                    "bound_strategy"        : "reflect-random"
                }

            The available options are:

            - **population_size** (int):  Initial population size (N). If set to `0`, it will be automatically determined. 
                .. math::

                        N = 5 \\cdot D

                where *D* is the dimensionality of the problem.
            - **mutation_strategy** (str):  Mutation strategy, default is "rand1", available : "rand1", "best1"
            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppABC`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppABC(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult
    

class Dual_Annealing(MinimizerBase):
    """
    Implementation of dual annealing algorithm.

    Reference : Tsallis C, Stariolo DA. Generalized Simulated Annealing. Physica A, 233, 395-406 (1996).

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 : list[list[float]]
            Initial guesses for the solution. If more than one initial guesses are provided, the code will pick the best one as the true initial guess.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "acceptance_par" : -5.0,  
                    "visit_par" :  2.67,  
                    "initial_temp"     :  5230.0, 
                    "restart_temp_ratio" : 2e-05,
                    "use_local_search": True,
                    "local_search_algo" : "L_BFGS_B",
                    "finite_diff_rel_step", 1e-10,
                    "bound_strategy"        : "periodic"
                }

            The available options are:

            - **acceptance_par** (double) : acceptance parameter. The value must be between -1.0e+4 and -5.
            - **visit_par** (double) : visiting distribution parameter. The value must be between 1.0 and 3.0.
            - **initial_temp** (double) : initial temperature. The value must be between 0.01 and 5.0e+4.
            - **restart_temp_ratio** (double) : restart temperature ratio. The value must be between 0 and 1.
            - **use_local_search** (bool) : a flag to whether or not to use local search. 
            - **local_search_algo** (str) : Algorithm name for local search. Available : "NelderMead" or "L_BFGS_B".
            - **finite_diff_rel_step** (double) : The relative step size for finite difference computations for L_BFGS_B. The default value 0.0 means that the relative step is given by the square root of machine epsilon. 
            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppDual_Annealing`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        if x0 is None : raise RuntimeError("x0 can not be none or empty.")
        self.optimizer = cppDual_Annealing(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult

class L_BFGS_B(MinimizerBase):
    """
    Implementation of L_BFGS_B algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 : list[list[float]]
            Initial guesses for the solution. If more than one initial guesses are provided, the code will pick the best one as the true initial guess.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "max_iterations": 0,
                    "m" : 15, 
                    "g_epsilon": 1e-8,
                    "g_epsilon_rel": 0.0,
                    "f_reltol": 1e-8,
                    "max_linesearch": 20,
                    "c_1": 1e-3,
                    "c_2": 0.9, 
                    "func_noise_ratio": 1e-16, 
                    "N_points_derivative": 3
                }

            The available options are:
            - **max_iterations** (int): Maximum number of iterations. Default is 0 (no limit).
            - **m** (int): The number of corrections used in the limited memory matrix. Default is 15.
            - **g_epsilon** (double): Absolute gradient tolerance for stopping criteria. Default is 1e-8.
            - **g_epsilon_rel** (double): Relative gradient tolerance for stopping criteria. Default is 0.0.
            - **f_reltol** (double): Relative function tolerance for stopping criteria. Default is 1e-8.
            - **max_linesearch** (int): Maximum number of line search steps per iteration. Default is 20.
            - **c_1** (double): Parameter for Armijo condition (sufficient decrease). Default is 1e-3.
            - **c_2** (double): Parameter for Wolfe condition (curvature condition). Default is 0.9.
            - **func_noise_ratio** (double): noise level ratio, defined by the ratio of noise/f. For smooth function, set to 0.0. 
            - **N_points_derivative** (int) : Number of points to calculate the numerical derivative. N=1 means forward difference, N>=2 use Lanczos noise-robust derivative. For smooth function, N=1 works well and use less function calls.


        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppL_BFGS_B`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        if x0 is None : raise RuntimeError("x0 can not be none or empty.")
        self.optimizer = cppL_BFGS_B(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult
    
class L_BFGS(MinimizerBase):
    """
    Implementation of L_BFGS algorithm for unconstrained optimization problem.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 x0: List[List[float]],
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        x0 : list[list[float]]
            Initial guesses for the solution. If more than one initial guesses are provided, the code will pick the best one as the true initial guess.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "max_iterations": 0,
                    "m" : 15, 
                    "g_epsilon": 1e-8,
                    "g_epsilon_rel": 0.0,
                    "f_reltol": 1e-8,
                    "max_linesearch": 20,
                    "c_1": 1e-3,
                    "c_2": 0.9, 
                    "func_noise_ratio": 1e-16, 
                    "N_points_derivative": 3
                }

            The available options are:
            - **max_iterations** (int): Maximum number of iterations. Default is 0 (no limit).
            - **m** (int): The number of corrections used in the limited memory matrix. Default is 15.
            - **g_epsilon** (double): Absolute gradient tolerance for stopping criteria. Default is 1e-8.
            - **g_epsilon_rel** (double): Relative gradient tolerance for stopping criteria. Default is 0.0.
            - **f_reltol** (double): Relative function tolerance for stopping criteria. Default is 1e-8.
            - **max_linesearch** (int): Maximum number of line search steps per iteration. Default is 20.
            - **c_1** (double): Parameter for Armijo condition (sufficient decrease). Default is 1e-3.
            - **c_2** (double): Parameter for Wolfe condition (curvature condition). Default is 0.9.
            - **func_noise_ratio** (double): noise level ratio, defined by the ratio of noise/f. For smooth function, set to 0.0. 
            - **N_points_derivative** (int) : Number of points to calculate the numerical derivative. N=1 means forward difference, N>=2 use Lanczos noise-robust derivative. For smooth function, N=1 works well and use less function calls.


        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppL_BFGS_B`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """
        bounds = [(-10,10)]*len(x0[0])
        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        if x0 is None : raise RuntimeError("x0 can not be none or empty.")
        self.optimizer = cppL_BFGS(self._func_for_cpp, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult
    
class j2020(MinimizerBase):
    """
    Implementation of the j2020 algorithm.

    Reference : J. Brest, M. S. Maučec and B. Bošković, "Differential Evolution Algorithm for Single Objective Bound-Constrained Optimization: Algorithm j2020," 2020 IEEE Congress on Evolutionary Computation (CEC), Glasgow, UK, 2020, pp. 1-8, doi: 10.1109/CEC48606.2020.9185551.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 :  list[list[float]], optional
            Initial guesses for the solution. These guesses will be used to initialize the population. 
            If None (default), a random initialization within the given bounds is used.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "population_size" : 0,  
                    "tau1"            : 0.1,
                    "tau2"            : 0.1 , 
                    "myEqs"           : 0.25,
                    "bound_strategy"  : "reflect-random"
                }

            The available options are:

            - **population_size** (int): Initial population size (N). If set to ``0``, it will be automatically determined as follows:

                .. math::

                        N = 8 \\cdot D

                where *D* is the dimensionality of the problem.
            - **tau1** (float) : The value of *tau1* variable. The value must be between 0 and 1. 
            - **tau2** (float) : The value of *tau1* variable. The value must be between 0 and 1. 
            - **myEqs** (float) : The value of *myEqs* variable. The value must be between 0 and 1. 
            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppj2020`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """


        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppj2020(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        return self.minionResult
    
class LSRTDE(MinimizerBase):
    """
    Implementation of the LSRTDE algorithm.

    Reference : V. Stanovov and E. Semenkin, "Success Rate-based Adaptive Differential Evolution L-SRTDE for CEC 2024 Competition," 2024 IEEE Congress on Evolutionary Computation (CEC), Yokohama, Japan, 2024, pp. 1-8, doi: 10.1109/CEC60901.2024.10611907.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 :  list[list[float]], optional
            Initial guesses for the solution. These guesses will be used to initialize the population. 
            If None (default), a random initialization within the given bounds is used.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "population_size"       : 0,  
                    "memory_size"           :  5,
                    "success_rate"          : 0.5 , 
                    "bound_strategy"        :"reflect-random"
                }

            The available options are:

            - **population_size** (int): Initial population size (N). If set to ``0``, it will be automatically determined as follows:

                .. math::

                        N = 20 \\cdot D

                where *D* is the dimensionality of the problem.

            - **memory_size** (float) : memory size for storing the values of ``CR`` and ``F`` 
            - **success_rate** (float) : The success rate value.
            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppLSRTDE`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """


        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppLSRTDE(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        return self.minionResult


class ARRDE(MinimizerBase):
    """
    Implementation of the Adaptive Restart Refine Differential Evolution (ARRDE) algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 :  list[list[float]], optional
            Initial guesses for the solution. These guesses will be used to initialize the population. 
            If None (default), a random initialization within the given bounds is used.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "population_size"           :  0,  
                    "minimum_population_size"   : 4,
                    "archive_size_ratio"        :  2.0, 
                    "converge_reltol"           :  0.005,
                    "refine_decrease_factor"    : 0.9, 
                    "restart-refine-duration"   : 0.8, 
                    "maximum_consecutive_restarts" : 2,
                    "bound_strategy"            : "reflect-random"
                }

            The available options are:

            - **population_size** (int): Initial population size (N). If set to ``0``, it will be automatically determined as follows:

                .. math::

                    N = 2 \\cdot D + \\log(N_{maxevals})^2

                where *D* is the dimensionality of the problem and :math:`N_{maxevals}` is the maximum number of function evaluations.
            - **minimum_population_size** (int) : final (minimum) population size during linear population size reduction.
            - **archive_size_ratio** (float) : the ratio of archive size to the current population size .
            - **converge_relTol** (float) : The value of std(f)/mean(f) below which a population is said to be converged.
            - **refine_decrease_factor** (float) : The decrease factor of *converge_relTol* in the refinement phase. 
            - **restart-refine-duration** (float) : a fraction of evaluation budget during which restart-refine phase occurs. The remaining fraction is dedicated to final refinement. 
            - **maximum_consecutive_restarts** (int) : maximum number of consecutive restarts during restart-refine phase.
            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppARRDE`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppARRDE(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.meanCR = self.optimizer.meanCR
        self.meanF = self.optimizer.meanF
        self.stdCR = self.optimizer.stdCR
        self.stdF = self.optimizer.stdF
        self.diversity = self.optimizer.diversity
        return self.minionResult


class Differential_Evolution(MinimizerBase):
    """
    Implementation of the vanilla (original) Differential Evolution algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python
        
                func(X) -> list[float]

            where `X` is a list of lists of floats.  
            Note that `func` is assumed to be vectorized. If the function instead  
            takes a single list of floats and returns a float,  
            it can be vectorized as follows (see examples in the documentation):

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

            
        bounds : list of tuple
            List of (min, max) pairs defining the bounds for each decision variable.
        x0 :  list[list[float]], optional
            Initial guesses for the solution. These guesses will be used to initialize the population. 
            If None (default), a random initialization within the given bounds is used.
        relTol : float, optional
            Relative tolerance for convergence. The algorithm stops if the relative 
            improvement in the objective function is below this value. Default is 1e-4.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is 100000.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            following settings are used::

                options = {
                    "population_size"         :  0,  
                    "mutation_strategy"       : "best1bin",
                    "mutation_rate"           : 0.5, 
                    "crossover_rate"          : 0.8,
                    "bound_strategy"          : "reflect-random"
                }

            The available options are:

            - **population_size** (int):  Initial population size (N). If set to `0`, it will be automatically determined. 
                .. math::

                        N = 5 \\cdot D

                where *D* is the dimensionality of the problem.
            - **mutation_strategy** (str):  Mutation strategy used in the optimization process. Available strategies:  
                    ``"best1bin"``, ``"best1exp"``, ``"rand1bin"``, ``"rand1exp"``,  
                    ``"current_to_pbest1bin"``, ``"current_to_pbest1exp"``.
            - **mutation_rate** (float): the value of the mutation rate (F).
            - **crossover_rate** (float): the value of the crossover rate (F).
            - **bound_strategy** (str): Method for handling boundary violations. Available strategies:  
                    ``"random"``, ``"reflect-random"``, ``"clip"``.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppDifferential_Evolution`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.

        """


        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppDifferential_Evolution(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.meanCR = self.optimizer.meanCR
        self.meanF = self.optimizer.meanF
        self.stdCR = self.optimizer.stdCR
        self.stdF = self.optimizer.stdF
        self.diversity = self.optimizer.diversity
        return self.minionResult
    
class Minimizer(MinimizerBase):
    """
    A general-purpose optimization class that encapsulates all optimization algorithms 
    implemented in Minion/py.

    This class provides an interface for various optimization algorithms, inheriting 
    from `MinimizerBase`. It allows users to minimize a given objective function using 
    different evolutionary and classical optimization techniques.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[List[float]]] = None,
                 algo : str = "ARRDE",
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = None
        ) : 
        """
        Initialize the algorithm.

        Parameters
        ----------
        func : callable
            The objective function to be minimized.

            .. code-block:: python

                func(X) -> list[float]

            where `X` is either:
            
            - A list of lists of floats (``list[list[float]]``)
    
            The function `func` is assumed to be vectorized. If it only supports a single 
            input (`list[float]` or `1D np.ndarray`), it can be vectorized as follows:

            .. code-block:: python 

                def func(X):
                    return [fun(x) for x in X]

        bounds : list of tuple
            List of `(min, max)` pairs defining the bounds for each decision variable.
        x0 : list[list[float]], optional
            Initial guesses for the solution. 
        algo : str, optional
            The optimization algorithm to use. Default is `"ARRDE"`.  
            Available algorithms include:

            - `"LSHADE"`
            - `"DE"`
            - `"JADE"`
            - `"jSO"`
            - `"NelderMead"`
            - `"LSRTDE"`
            - `"NLSHADE_RSP"`
            - `"j2020"`
            - `"GWO_DE"`
            - `"ARRDE"` 
            - `"ABC"` (artificial bee colony)
            - `"DA"` (dual annealing)
            - `"L_BFGS_B"` 
            - `"L_BFGS"` 

        relTol : float, optional
            Relative tolerance for convergence. The optimization stops if the relative 
            improvement in the objective function is below this threshold. Default is `1e-4`.
        maxevals : int, optional
            Maximum number of function evaluations allowed. Default is `100000`.
        callback : callable, optional
            A function that is called after each iteration. It must accept a single 
            argument containing the current optimization state. Default is None.
        seed : int, optional
            Random seed for reproducibility. If None (default), the seed is not set.
        options : dict, optional
            Additional options for configuring the algorithm. If None (default), the 
            settings are taken from the default configuration of the chosen algorithm.

        Notes
        -----
        - The optimizer is implemented in C++ and accessed via `cppMinimizer`.
        - The `callback` function can be used for logging or monitoring progress.
        - The `options` dictionary allows fine-tuning of the optimization process.
        """
        all_algo = [
            "lshade", "de", "jade", "jso", "neldermead", "lsrtde",
            "nlshade_rsp", "j2020", "gwo_de", "arrde", "abc", "da",
            "l_bfgs_b", "l_bfgs", "lshade_cnepsin", "pso", "spso2011", "dmspso", "cmaes", "bipop_acmaes"
        ]

        algo_lower = algo.lower()

        if algo_lower not in all_algo:
            raise Exception("Unknown algorithm. The algorithm must be one of these:", all_algo)

        if algo_lower in ["neldermead", "da", "l_bfgs", "l_bfgs_b"] and (x0 is None):
            raise RuntimeError("x0 must not be None or empty for Nelder-Mead to work!")
        
        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppMinimizer(self._func_for_cpp, self.bounds, self.x0cpp, self.data, self._callback_for_cpp, algo_lower, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        Run the optimization algorithm.

        Returns
        -------
        MinionResult
            The optimization result containing the best solution found.

        Notes
        -----
        This method runs the optimization algorithm and stores the result 
        in `self.minionResult`. The optimization history is also stored in 
        `self.history`, containing intermediate results at each iteration.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult
