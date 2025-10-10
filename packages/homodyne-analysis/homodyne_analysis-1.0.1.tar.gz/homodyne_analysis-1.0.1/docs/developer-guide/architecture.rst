Package Architecture
====================

This document describes the overall architecture and design patterns used in the homodyne package.

Core Architecture
-----------------

The package follows a layered architecture:

.. code-block:: text

   User Interface Layer
   ├── CLI Scripts (run_homodyne.py)
   └── Python API (HomodyneAnalysisCore)
           │
   Analysis Layer
   ├── Configuration Management
   ├── Data Loading & Validation
   └── Result Generation
           │
   Optimization Layer
   ├── Classical Optimization (Nelder-Mead, Iterative Gurobi Trust Region)
   ├── Robust Optimization (Wasserstein DRO, Scenario-based, Ellipsoidal)
           │
   Model Layer
   ├── Physical Models
   └── Mathematical Functions
           │
   Utility Layer
   ├── Data I/O
   ├── Plotting
   └── Error Handling

Key Components
--------------

**1. Configuration System**

.. code-block:: python

   class ConfigManager:
       """Centralized configuration management"""
       def __init__(self, config_path: str)
       def validate(self) -> bool
       def get_analysis_settings(self) -> dict

**2. Analysis Core**

.. code-block:: python

   class HomodyneAnalysisCore:
       """Main analysis orchestrator"""
       def __init__(self, config: ConfigManager)
       def load_experimental_data(self)
       def optimize_classical(self) -> OptimizeResult
       def optimize_robust(self) -> dict
       def optimize_all(self) -> dict

**3. Model System**

.. code-block:: python

   # Functional interface for models
   def static_isotropic_model(tau, params, q)
   def static_anisotropic_model(tau, params, q, phi)
   def laminar_flow_model(tau, params, q, phi)

**4. Optimization Backends**

.. code-block:: python

   class ClassicalOptimizer:
       """SciPy and Gurobi-based optimization"""

   class RobustHomodyneOptimizer:
       """CVXPY-based robust optimization"""


**5. Gurobi Trust Region Implementation**

The Gurobi optimization uses an iterative trust region approach for enhanced convergence:

.. code-block:: python

   def _run_gurobi_optimization(self, objective_func, initial_parameters):
       """
       Iterative trust region SQP optimization:
       1. Build quadratic approximation around current point
       2. Solve QP subproblem with trust region constraints
       3. Evaluate actual objective and update trust region
       4. Iterate until convergence
       """
       x_current = initial_parameters.copy()
       trust_radius = 0.1  # Initial trust region

       for iteration in range(max_iterations):
           # Estimate gradient and diagonal Hessian
           grad = self._compute_gradient(objective_func, x_current)
           hessian_diag = self._compute_hessian_diagonal(objective_func, x_current)

           # Solve trust region QP subproblem with Gurobi
           step = self._solve_trust_region_qp(grad, hessian_diag, trust_radius)

           # Evaluate and accept/reject step
           x_new = x_current + step
           if objective_func(x_new) < objective_func(x_current):
               x_current = x_new  # Accept step
               trust_radius = min(1.0, 2 * trust_radius)  # Expand region
           else:
               trust_radius = max(1e-8, 0.5 * trust_radius)  # Shrink region

Design Patterns
---------------

**1. Strategy Pattern** - Optimization Methods

Different optimization strategies are encapsulated:

.. code-block:: python

   class OptimizationStrategy(ABC):
       @abstractmethod
       def optimize(self, objective_func, initial_params):
           pass

   class NelderMeadStrategy(OptimizationStrategy):
       def optimize(self, objective_func, initial_params):
           return minimize(objective_func, initial_params, method='Nelder-Mead')

       def optimize(self, objective_func, initial_params):

**2. Factory Pattern** - Model Creation

Models are created based on configuration:

.. code-block:: python

   class ModelFactory:
       @staticmethod
       def create_model(analysis_mode: str):
           if analysis_mode == "static_isotropic":
               return StaticIsotropicModel()
           elif analysis_mode == "laminar_flow":
               return LaminarFlowModel()
           else:
               raise ValueError(f"Unknown mode: {analysis_mode}")

**3. Observer Pattern** - Progress Tracking

.. code-block:: python

   class ProgressObserver:
       def update(self, stage: str, progress: float):
           pass

   class ConsoleProgressObserver(ProgressObserver):
       def update(self, stage: str, progress: float):
           print(f"{stage}: {progress:.1%}")

**4. Command Pattern** - Analysis Pipeline

.. code-block:: python

   class AnalysisCommand(ABC):
       @abstractmethod
       def execute(self):
           pass

   class LoadDataCommand(AnalysisCommand):
       def execute(self):
           # Load experimental data

   class OptimizeCommand(AnalysisCommand):
       def execute(self):
           # Run optimization

Data Flow
---------

.. code-block:: text

   Configuration File
         │
         ▼
   ConfigManager ────────────► Validation
         │
         ▼
   HomodyneAnalysisCore ─────► Data Loading
         │
         ▼
   Model Selection ──────────► Parameter Setup
         │
         ▼
         │
         ▼
   Results Processing ───────► Output Generation

Error Handling Strategy
-----------------------

**Hierarchical Error Classes**:

.. code-block:: python

   class HomodyneError(Exception):
       """Base exception for all homodyne errors"""

   class ConfigurationError(HomodyneError):
       """Configuration-related errors"""

   class DataFormatError(HomodyneError):
       """Data format and loading errors"""

   class OptimizationError(HomodyneError):
       """Optimization convergence errors"""


**Error Recovery**:

.. code-block:: python

   def robust_optimization(self):
       """Optimization with fallback strategies"""
       try:
           return self.primary_optimization()
       except OptimizationError:
           logger.warning("Primary optimization failed, trying fallback")
           return self.fallback_optimization()

Performance Architecture
------------------------

**1. Lazy Loading**

Data and computations are loaded only when needed:

.. code-block:: python

   class LazyDataLoader:
       def __init__(self, file_path):
           self.file_path = file_path
           self._data = None

       @property
       def data(self):
           if self._data is None:
               self._data = load_data_file(self.file_path)
           return self._data

**2. Caching Strategy**

Expensive computations are cached:

.. code-block:: python

   from functools import lru_cache

   @lru_cache(maxsize=128)
   def compute_model_expensive(tau_tuple, params_tuple, q):
       # Expensive model computation
       pass

**3. Parallel Processing**


.. code-block:: python

   from concurrent.futures import ProcessPoolExecutor
   import multiprocessing

   # Parallel data processing
   num_workers = multiprocessing.cpu_count()

   with ProcessPoolExecutor(max_workers=num_workers) as executor:
       results = executor.map(process_angle_data, angle_chunks)

   # Parallel optimization runs
   with ProcessPoolExecutor(max_workers=4) as executor:
       optimization_results = executor.map(
           run_optimization,
           parameter_sets
       )

Plugin Architecture
-------------------

The package supports extensions through plugins:

.. code-block:: python

   class ModelPlugin(ABC):
       @abstractmethod
       def get_model_name(self) -> str:
           pass

       @abstractmethod
       def compute_correlation(self, tau, params, q, phi=None):
           pass

   class CustomFlowModel(ModelPlugin):
       def get_model_name(self) -> str:
           return "custom_flow"

       def compute_correlation(self, tau, params, q, phi=None):
           # Custom model implementation
           pass

Testing Architecture
--------------------

**Test Organization**:

.. code-block:: text

   tests/
   ├── unit/                    # Unit tests for individual components
   │   ├── test_config.py
   │   ├── test_models.py
   │   └── test_optimization.py
   ├── integration/             # Integration tests
   │   ├── test_full_workflow.py
   └── fixtures/                # Test data and fixtures
       ├── sample_config.json
       └── test_data.h5

**Test Fixtures**:

.. code-block:: python

   @pytest.fixture
   def sample_config():
       return {
           "analysis_settings": {
               "static_mode": True,
               "static_submode": "isotropic"
           },
           "initial_parameters": {
               "values": [1000, -0.5, 100]
           }
       }

   @pytest.fixture
   def synthetic_data():
       tau = np.logspace(-6, 1, 100)
       g1 = np.exp(-tau**0.8)
       return tau, g1

Memory Management
-----------------

**Large Dataset Handling**:

.. code-block:: python

   class ChunkedDataProcessor:
       def __init__(self, chunk_size: int = 1000):
           self.chunk_size = chunk_size

       def process_large_dataset(self, data):
           for chunk in self.chunk_data(data):
               yield self.process_chunk(chunk)

       def chunk_data(self, data):
           for i in range(0, len(data), self.chunk_size):
               yield data[i:i + self.chunk_size]

**Memory Monitoring**:

.. code-block:: python

   import psutil

   def monitor_memory_usage(func):
       def wrapper(*args, **kwargs):
           initial_memory = psutil.Process().memory_info().rss / 1024**2
           result = func(*args, **kwargs)
           final_memory = psutil.Process().memory_info().rss / 1024**2
           print(f"Memory usage: {final_memory - initial_memory:.1f} MB")
           return result
       return wrapper

Future Architecture Considerations
----------------------------------

1. **Distributed Computing**: Support for multi-node cluster computing
2. **Advanced CPU Optimization**: Further vectorization and JIT improvements
3. **Streaming Data**: Real-time analysis capabilities
4. **Cloud Integration**: Cloud storage and computing support
5. **Web Interface**: Browser-based analysis frontend
