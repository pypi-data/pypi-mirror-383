Performance Optimization
=========================

This guide covers performance optimization strategies for the homodyne package.

.. note::
   **NEW**: See the comprehensive :doc:`../performance` guide for the latest performance improvements,
   including recent optimizations that delivered 10-17x speedups in key calculations.

.. toctree::
   :maxdepth: 1
   :caption: Performance Documentation

   ../performance

Performance Overview
--------------------

The homodyne package is designed to handle large datasets efficiently. Key performance considerations:

- **Memory Management**: Efficient handling of large correlation matrices
- **Computational Optimization**: Numba JIT compilation and vectorization
- **Algorithm Selection**: Optimizing Nelder-Mead configuration

Optimization Strategies
-----------------------

**1. Angle Filtering**

The most effective optimization for speed with minimal accuracy loss:

.. code-block:: python

   # Performance improvement: 3-5x speedup
   config = {
       "analysis_settings": {
           "enable_angle_filtering": True,
           "angle_filter_ranges": [[-5, 5], [175, 185]]
       }
   }

**Benefits**:
- 3-5x faster computation
- < 1% accuracy loss for most systems
- Reduced memory usage
- Scales well with dataset size

**2. Data Type Optimization**

Choose appropriate precision for your needs:

.. code-block:: python

   # Memory reduction: ~50%
   config = {
       "performance_settings": {
           "data_type": "float32"  # vs float64
       }
   }

.. list-table:: Data Type Comparison
   :widths: 15 15 15 25 30
   :header-rows: 1

   * - Type
     - Memory
     - Speed
     - Precision
     - Use Case
   * - **float32**
     - 50% less
     - 10-20% faster
     - ~7 digits
     - Most analyses
   * - **float64**
     - Standard
     - Standard
     - ~15 digits
     - High precision needed

**3. JIT Compilation**

Enable Numba for computational functions:

.. code-block:: python

   from numba import jit

   @jit(nopython=True, cache=True)
   def compute_correlation_fast(tau, params, q):
       # JIT-compiled computation
       # 5-10x speedup for model functions
       pass

**4. Parallel Optimization**

Configure parallel processing for optimization:

.. code-block:: python

   config = {
       "performance_settings": {
           "num_threads": 4,              # Match CPU cores
           "enable_jit": True,            # Numba JIT compilation
           "data_type": "float64",        # Precision vs memory tradeoff
           "memory_limit_gb": 8           # Memory constraints
       },
       "optimization_config": {
           "classical_optimization": {
               "methods": ["Nelder-Mead"],
               "method_options": {
                   "Nelder-Mead": {
                       "maxiter": 5000,
                       "xatol": 1e-6,
                       "fatol": 1e-6
                   }
               }
           }
       }
   }

**Optimization Performance Tips**:

- **Use angle filtering**: 3-4x speedup for anisotropic analysis
- **Enable JIT compilation**: 3-5x speedup for core computations
- **Reduce precision**: Use float32 for 2x memory reduction
- **Batch processing**: Process multiple samples in parallel

Memory Optimization
-------------------

**1. Memory Estimation**

Estimate memory requirements before analysis:

.. code-block:: python

   from homodyne.utils import estimate_memory_usage

   memory_gb = estimate_memory_usage(
       data_shape=(1000, 500),    # Time points x angles
       num_angles=360,
       analysis_mode="laminar_flow",
       data_type="float64"
   )

   print(f"Estimated memory: {memory_gb:.1f} GB")

**2. Chunked Processing**

For very large datasets:

.. code-block:: python

   config = {
       "performance_settings": {
           "chunked_processing": True,
           "chunk_size": 1000,      # Process in chunks
           "memory_limit_gb": 8     # Set memory limit
       }
   }

**3. Memory Monitoring**

Monitor memory usage during analysis:

.. code-block:: python

   import psutil

   def monitor_memory():
       process = psutil.Process()
       memory_mb = process.memory_info().rss / 1024**2
       print(f"Memory usage: {memory_mb:.1f} MB")

   # Use during analysis
   analysis.load_experimental_data()
   monitor_memory()

   result = analysis.optimize_classical()
   monitor_memory()

CPU Optimization
----------------

**1. Thread Configuration**

Optimize thread usage:

.. code-block:: python

   import os

   # Set thread counts
   os.environ['OMP_NUM_THREADS'] = '4'
   os.environ['NUMBA_NUM_THREADS'] = '4'

   config = {
       "performance_settings": {
           "num_threads": 4  # Match your CPU cores
       }
   }

**2. BLAS/LAPACK Optimization**

Use optimized linear algebra libraries:

.. code-block:: bash

   # Install optimized BLAS
   conda install mkl
   # or
   pip install intel-mkl

**3. CPU Profiling**

Profile CPU usage to identify bottlenecks:

.. code-block:: python

   import cProfile
   import pstats

   # Profile analysis
   profiler = cProfile.Profile()
   profiler.enable()

   # Run analysis
   result = analysis.optimize_classical()

   profiler.disable()
   stats = pstats.Stats(profiler)
   stats.sort_stats('cumulative').print_stats(10)

Algorithm Optimization
----------------------

**1. Optimization Method Selection**

Choose appropriate optimization algorithms:

.. code-block:: python

   # Fast for simple landscapes
   config = {
       "optimization_config": {
           "classical": {
               "method": "Nelder-Mead",  # Fast, robust
               "max_iterations": 1000
           }
       }
   }

   # For complex landscapes
   config = {
       "optimization_config": {
           "classical_optimization": {
               "methods": ["Nelder-Mead"],     # Derivative-free simplex method
               "method_options": {
                   "Nelder-Mead": {"maxiter": 500}
               }
           }
       }
   }

**2. Optimization Strategy by Analysis Mode**

Configure optimization parameters based on problem complexity:

.. code-block:: python

   # Static Isotropic Mode (3 parameters)
   config = {
       "optimization_config": {
           "classical_optimization": {
               "methods": ["Nelder-Mead"],
               "method_options": {
                   "Nelder-Mead": {
                       "maxiter": 2000,      # Faster convergence
                       "xatol": 1e-6,
                       "fatol": 1e-6
                   }
               }
           }
       },
       "performance_settings": {
           "num_threads": 4,
           "enable_jit": True
       }
   }

   # Static Anisotropic Mode (3 parameters)
   config = {
       "optimization_config": {
           "classical_optimization": {
               "methods": ["Nelder-Mead"],
               "method_options": {
                   "Nelder-Mead": {
                       "maxiter": 3000,      # More iterations for angular dependence
                       "xatol": 1e-6,
                       "fatol": 1e-6
                   }
               }
           }
       },
       "analysis_settings": {
           "enable_angle_filtering": True,   # 3-5x speedup
           "angle_filter_ranges": [[-5, 5], [175, 185]]
       }
   }

   # Laminar Flow Mode (7 parameters)
   config = {
       "optimization_config": {
           "classical_optimization": {
               "methods": ["Nelder-Mead"],
               "method_options": {
                   "Nelder-Mead": {
                       "maxiter": 5000,      # More iterations for complex landscape
                       "xatol": 1e-7,        # Tighter tolerance
                       "fatol": 1e-7
                   }
               }
           }
       },
       "performance_settings": {
           "num_threads": 8,              # More parallelism
           "enable_jit": True,
           "data_type": "float64"         # Higher precision needed
       }
   }

Performance Benchmarks
----------------------

**Typical Performance Metrics**:

.. list-table:: Performance Benchmarks
   :widths: 25 15 15 15 30
   :header-rows: 1

   * - Configuration
     - Time
     - Memory
     - Speedup
     - Notes
   * - **Basic isotropic**
     - 30s
     - 0.5 GB
     - 1x
     - Baseline
   * - **+ Angle filtering**
     - 8s
     - 0.3 GB
     - 4x
     - Most effective
   * - **+ Float32**
     - 7s
     - 0.15 GB
     - 4.3x
     - Memory efficient
   * - **+ JIT compilation**
     - 5s
     - 0.15 GB
     - 6x
     - Full optimization

Profiling Tools
---------------

**1. Time Profiling**

.. code-block:: python

   import time
   from functools import wraps

   def time_it(func):
       @wraps(func)
       def wrapper(*args, **kwargs):
           start = time.time()
           result = func(*args, **kwargs)
           end = time.time()
           print(f"{func.__name__}: {end - start:.2f}s")
           return result
       return wrapper

   @time_it
   def optimize_classical(self):
       # Timed function
       pass

**2. Memory Profiling**

.. code-block:: python

   from memory_profiler import profile

   @profile
   def analyze_data():
       # Memory-profiled function
       pass

**3. Line Profiling**

.. code-block:: bash

   # Install line_profiler
   pip install line_profiler

   # Profile specific functions
   kernprof -l -v my_script.py

Performance Best Practices
---------------------------

**Configuration**:

1. **Enable angle filtering** for 3-5x speedup
2. **Use float32** unless high precision needed
3. **Set appropriate thread counts** (match CPU cores)
4. **Enable JIT compilation** for model functions

**Optimization**:

1. **Start with classical optimization** (Nelder-Mead) for reliable convergence
2. **Use appropriate maxiter** based on problem complexity (2000-5000)
3. **Set proper tolerance** (xatol/fatol: 1e-6 to 1e-7)
4. **Verify convergence** by checking optimization success flag
5. **Use good initial guesses** from physical constraints or previous results
6. **Enable parallel processing** for multi-sample analyses

**Memory**:

1. **Estimate memory needs** before large analyses
2. **Use chunked processing** for very large datasets
3. **Monitor memory usage** during long runs
4. **Clean up intermediate results** when possible

**Development**:

1. **Profile before optimizing** to find real bottlenecks
2. **Test performance changes** with realistic datasets
3. **Balance speed vs. accuracy** based on requirements
4. **Document performance characteristics** of new features

Troubleshooting Performance Issues
----------------------------------

**Slow Optimization**:

1. Enable angle filtering
2. Check initial parameter values
3. Adjust Nelder-Mead optimization parameters
4. Reduce tolerance if acceptable

**High Memory Usage**:

1. Use float32 data type
2. Enable chunked processing
3. Reduce dataset size if possible
4. Check for memory leaks

**Poor Convergence**:

1. Increase maximum iterations (maxiter)
2. Adjust tolerance parameters (xatol, fatol)
3. Check parameter bounds and constraints
4. Use better initial values from physical estimates
5. Try multiple optimization runs with different initial conditions
6. Consider robust optimization for noisy data

**System-Specific Issues**:

1. Check BLAS/LAPACK installation
2. Verify thread settings
3. Monitor CPU/memory resources
4. Consider cluster computing for very large problems
