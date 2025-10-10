Utilities
=========

Utility functions for data handling, validation, and common operations.

Data Handling
-------------

**save_json(data, filepath)**

Save data in JSON format with NumPy array support.

**save_numpy(data, filepath)**

Save analysis results as NumPy compressed files.

**save_analysis_results(results, output_dir)**

Save complete analysis results in multiple formats.

File System Utilities
---------------------

**ensure_dir(path)**

Create directories with proper permissions.

**timestamped_filename(base_name, ext=".json")**

Generate timestamped filenames for results.

Configuration Utilities
------------------------

**ConfigManager**

Configuration management with validation and template support.

**configure_logging(level="INFO", log_file=None)**

Configure logging for analysis sessions.

Performance Utilities
----------------------

**memory_efficient_cache(maxsize=128)**

Memory-efficient caching decorator for expensive computations.

**exp_negative_vectorized(array)**

Optimized vectorized exponential operations.

Plotting Utilities
------------------

**plot_c2_heatmaps(data, angles, time_points)**

Plot experimental correlation data as heatmaps.






Usage Examples
--------------

**Data I/O Operations**:

.. code-block:: python

   from homodyne.core.io_utils import (
       save_json, save_numpy, save_analysis_results,
       ensure_dir, timestamped_filename
   )

   # Ensure output directory exists
   output_dir = ensure_dir("results/experiment_1")

   # Generate timestamped filename
   filename = timestamped_filename("analysis_results", ext=".json")

   # Save results in multiple formats
   save_json(results_dict, f"{output_dir}/{filename}")
   save_analysis_results(analysis_results, output_dir)

**Configuration Management**:

.. code-block:: python

   from homodyne import ConfigManager
   from homodyne.core.config import configure_logging

   # Configure logging
   configure_logging(level="INFO", log_file="analysis.log")

   # Initialize configuration manager
   config = ConfigManager("experiment_config.json")

   # Access configuration settings
   analysis_mode = config.get_analysis_mode()
   active_params = config.get_active_parameters()

   print(f"Analysis mode: {analysis_mode}")
   print(f"Active parameters: {active_params}")

**High-Performance Computing**:

.. code-block:: python

   from homodyne import (
       memory_efficient_cache, exp_negative_vectorized,
       performance_monitor
   )

   # Use memory-efficient caching
   @memory_efficient_cache(maxsize=128)
   def expensive_computation(data):
       return complex_analysis(data)

   # Optimized vectorized operations
   result = exp_negative_vectorized(large_array)

   # Monitor performance
   with performance_monitor() as monitor:
       analysis_result = run_analysis()

   print(f"Analysis completed in {monitor.elapsed_time:.2f}s")

**Results Visualization**:

.. code-block:: python

   from homodyne.core.io_utils import save_fig

   # Plot correlation data heatmaps
   fig1 = plot_c2_heatmaps(
       experimental_data, phi_angles, time_points
   )
   save_fig(fig1, "correlation_heatmaps.png", dpi=300)


       # Trace plots for convergence

File I/O Functions
------------------

**get_output_directory(config=None)**

Get organized output directory structure based on configuration settings.

**save_fig(fig, filepath, dpi=300, bbox_inches='tight')**

Save matplotlib figures with proper formatting and publication-quality settings.

**Error Handling Example**:

.. code-block:: python

   from homodyne import ConfigManager, HomodyneAnalysisCore
   import logging

   # Configure logging for better error tracking
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   try:
       config = ConfigManager("config.json")
       config.validate_config()  # Validate configuration

       analysis = HomodyneAnalysisCore(config)
       analysis.load_experimental_data()
       results = analysis.run_analysis()

       logger.info(f"Analysis completed successfully with {len(results)} results")

   except FileNotFoundError as e:
       logger.error(f"Configuration file not found: {e}")
   except ValueError as e:
       logger.error(f"Configuration validation error: {e}")
   except ImportError as e:
       logger.error(f"Missing dependencies: {e}")
   except Exception as e:
       logger.error(f"Unexpected error during analysis: {e}")
