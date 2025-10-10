"""
CLI Optimization Module
=======================

Optimization execution functions for the homodyne CLI interface.

This module contains the optimization workflow functions that handle the execution
of classical and robust optimization methods, including result processing and
validation.
"""

import logging

import numpy as np

# Module-level logger
logger = logging.getLogger(__name__)


def run_classical_optimization(
    analyzer, initial_params, phi_angles, c2_exp, output_dir=None
):
    """
    Execute classical optimization using traditional methods only.

    This function is called by --method classical and runs ONLY:
    - Nelder-Mead (always available)
    - Gurobi (if available and licensed)

    It explicitly EXCLUDES robust methods (Robust-Wasserstein, Robust-Scenario,
    Robust-Ellipsoidal) which are run separately via --method robust.

    Provides fast parameter estimation with point estimates and goodness-of-fit
    statistics. Uses intelligent angle filtering for performance on large datasets.

    Parameters
    ----------
    analyzer : HomodyneAnalysisCore
        Main analysis engine with loaded configuration
    initial_params : list
        Starting parameter values for optimization
    phi_angles : ndarray
        Angular coordinates for the scattering data
    c2_exp : ndarray
        Experimental correlation function data
    output_dir : Path, optional
        Directory for saving classical results and fitted data

    Returns
    -------
    dict or None
        Results dictionary with optimized parameters and fit statistics,
        or None if optimization fails
    """
    logger.info(
        "Running classical optimization... [CODE-VERSION: 2024-09-30-v2-empty-array-fix]"
    )

    try:
        # Import here to avoid circular imports
        from ..optimization.classical import ClassicalOptimizer

        if ClassicalOptimizer is None:
            logger.error(
                "❌ ClassicalOptimizer is not available. Please ensure the "
                "homodyne.optimization.classical module is installed and accessible."
            )
            return None

        # Use enhanced optimizer if available, otherwise use standard optimizer
        if (
            hasattr(analyzer, "_enhanced_classical_optimizer")
            and analyzer._enhanced_classical_optimizer is not None
        ):
            logger.info("✓ Using enhanced classical optimizer")
            optimizer = analyzer._enhanced_classical_optimizer
        else:
            logger.info("✓ Creating new classical optimizer")
            optimizer = ClassicalOptimizer(analyzer, analyzer.config)

        # Validate data shapes before optimization
        if c2_exp is None or len(c2_exp) == 0:
            logger.error("❌ No experimental data provided for optimization")
            return None

        if phi_angles is None or len(phi_angles) == 0:
            logger.error("❌ No phi angles provided for optimization")
            return None

        # Check data consistency
        expected_shape = (len(phi_angles), c2_exp.shape[1], c2_exp.shape[2])
        if c2_exp.shape != expected_shape:
            logger.warning(
                f"⚠️  Data shape mismatch: expected {expected_shape}, got {c2_exp.shape}"
            )

        # Run the optimization (with return_tuple=True to get scipy result object)
        logger.debug("About to call run_optimization with return_tuple=True")
        params, result = optimizer.run_optimization(
            initial_params=initial_params,
            phi_angles=phi_angles,
            c2_experimental=c2_exp,
            return_tuple=True,
        )
        logger.debug(
            f"run_optimization returned: params type={type(params)}, "
            f"params={params if params is None else f'array[{len(params)}]'}, "
            f"result type={type(result)}"
        )

        if result is None or params is None:
            logger.error("❌ Classical optimization returned no result (None values)")
            logger.error(f"  params is None: {params is None}")
            logger.error(f"  result is None: {result is None}")
            return None

        # Validate optimization result - check multiple conditions
        if not hasattr(result, "x"):
            logger.error("❌ Optimization result has no 'x' attribute")
            return None

        if result.x is None:
            logger.error("❌ Optimization result.x is None")
            return None

        if not isinstance(result.x, np.ndarray):
            logger.error(f"❌ Optimization result.x is not ndarray: {type(result.x)}")
            return None

        if result.x.size == 0 or len(result.x) == 0:
            logger.error(
                f"❌ Optimization result.x is empty: size={result.x.size}, len={len(result.x)}"
            )
            logger.error(f"  result.success={getattr(result, 'success', 'N/A')}")
            logger.error(f"  result.message={getattr(result, 'message', 'N/A')}")
            logger.error(f"  result.nit={getattr(result, 'nit', 'N/A')}")
            logger.error(f"  result.nfev={getattr(result, 'nfev', 'N/A')}")
            return None

        logger.info("✓ Classical optimization completed successfully")
        logger.info(f"✓ Final chi-squared: {result.fun:.6f}")
        logger.info(f"✓ Optimization success: {result.success}")

        # Log parameters
        param_names = analyzer.config.get(
            "parameter_names", [f"p{i}" for i in range(len(result.x))]
        )
        for i, (name, value) in enumerate(zip(param_names, result.x, strict=False)):
            logger.info(f"✓ {name}: {value:.6f}")

        # Extract individual method results if available
        all_classical_results = {}
        if hasattr(result, "method_results"):
            logger.info("")
            logger.info("=" * 50)
            logger.info("CLASSICAL METHODS SUMMARY")
            logger.info("=" * 50)

            for method_name, method_data in result.method_results.items():
                if method_data.get("success", False) and method_data.get("parameters"):
                    logger.info(
                        f"{method_name:15s}: χ² = {method_data['chi_squared']:.6f}, "
                        f"success = {method_data['success']}"
                    )

                    # Create result dict for this method
                    all_classical_results[method_name.lower().replace("-", "_")] = {
                        "method": method_name.lower().replace("-", "_"),
                        "parameters": np.array(method_data["parameters"]),
                        "chi_squared": method_data["chi_squared"],
                        "success": method_data["success"],
                        "result_object": {
                            "iterations": method_data.get("iterations"),
                            "function_evaluations": method_data.get(
                                "function_evaluations"
                            ),
                            "message": method_data.get("message", ""),
                            "method": method_data.get("method", method_name),
                        },
                    }

            if hasattr(result, "best_method"):
                logger.info("")
                logger.info(
                    f"⭐ Best method: {result.best_method} (χ² = {result.fun:.6f})"
                )
            logger.info("=" * 50)

        return {
            "method": "classical",
            "parameters": result.x,
            "chi_squared": result.fun,
            "success": result.success,
            "result_object": result,
            "all_classical_results": all_classical_results,  # Include all method results
        }

    except Exception as e:
        logger.error(f"❌ Classical optimization failed: {e}")
        import traceback

        logger.debug(f"Full traceback: {traceback.format_exc()}")
        return None


def run_robust_optimization(
    analyzer, initial_params, phi_angles, c2_exp, output_dir=None
):
    """
    Execute robust optimization using uncertainty-aware methods only.

    This function is called by --method robust and runs ONLY:
    - Robust-Wasserstein (Distributionally Robust Optimization)
    - Robust-Scenario (Bootstrap-based)
    - Robust-Ellipsoidal (Bounded uncertainty)

    It explicitly EXCLUDES classical methods (Nelder-Mead, Gurobi) which are
    run separately via --method classical.

    Provides noise-resistant parameter estimation with uncertainty quantification
    and outlier robustness. Automatically handles data uncertainty and measurement
    noise for experimental robustness.

    Parameters
    ----------
    analyzer : HomodyneAnalysisCore
        Main analysis engine with loaded configuration
    initial_params : list
        Starting parameter values for optimization
    phi_angles : ndarray
        Angular coordinates for the scattering data
    c2_exp : ndarray
        Experimental correlation function data
    output_dir : Path, optional
        Directory for saving robust results and uncertainty plots

    Returns
    -------
    dict or None
        Results dictionary with robust parameters and uncertainty bounds,
        or None if optimization fails
    """
    logger.info("Running robust optimization...")

    try:
        # Import here to avoid circular imports
        from ..optimization.robust import create_robust_optimizer

        if create_robust_optimizer is None:
            logger.error(
                "❌ Robust optimization is not available. Please ensure the "
                "homodyne.optimization.robust module is installed and accessible."
            )
            return None

        # Use enhanced optimizer if available, otherwise create new one
        if (
            hasattr(analyzer, "_enhanced_robust_optimizer")
            and analyzer._enhanced_robust_optimizer is not None
        ):
            logger.info("✓ Using enhanced robust optimizer")
            optimizer = analyzer._enhanced_robust_optimizer
        else:
            logger.info("✓ Creating new robust optimizer with caching enabled")
            # Caching now uses safe_hash_object to handle unpicklable objects like RLock
            optimizer = create_robust_optimizer(
                analyzer, analyzer.config, enable_caching=True
            )

        # Validate data shapes before optimization
        if c2_exp is None or len(c2_exp) == 0:
            logger.error("❌ No experimental data provided for optimization")
            return None

        if phi_angles is None or len(phi_angles) == 0:
            logger.error("❌ No phi angles provided for optimization")
            return None

        # Check data consistency
        expected_shape = (len(phi_angles), c2_exp.shape[1], c2_exp.shape[2])
        if c2_exp.shape != expected_shape:
            logger.warning(
                f"⚠️  Data shape mismatch: expected {expected_shape}, got {c2_exp.shape}"
            )

        # Run all three robust optimization methods
        robust_methods = ["wasserstein", "scenario", "ellipsoidal"]
        all_results = {}
        best_result = None
        best_chi_squared = float("inf")

        logger.info("=" * 50)
        logger.info("Running all robust optimization methods...")
        logger.info("=" * 50)

        for method in robust_methods:
            logger.info("")
            logger.info(f"ROBUST METHOD: {method.upper()}")
            logger.info("-" * 30)

            try:
                # Run the robust optimization with specific method
                # Returns tuple: (optimal_parameters, optimization_info_dict)
                parameters, result_info = optimizer.run_robust_optimization(
                    initial_parameters=initial_params,
                    phi_angles=phi_angles,
                    c2_experimental=c2_exp,
                    method=method,
                )

                if parameters is None or result_info is None:
                    logger.warning(
                        f"⚠️  {method.capitalize()} optimization returned no result"
                    )
                    continue

                # Validate parameters
                if not isinstance(parameters, np.ndarray) or len(parameters) == 0:
                    logger.warning(
                        f"⚠️  {method.capitalize()} returned invalid parameters: "
                        f"type={type(parameters)}"
                    )
                    continue

                # Extract chi-squared from result_info
                chi_squared = result_info.get(
                    "chi_squared",
                    result_info.get(
                        "final_chi_squared", result_info.get("final_cost", 0.0)
                    ),
                )
                if chi_squared is None:
                    chi_squared = 0.0

                result_info.get("method", method)
                success = result_info.get("success", True)

                logger.info(f"✓ {method.capitalize()} optimization completed")
                if chi_squared > 0:
                    logger.info(f"✓ Final chi-squared: {chi_squared:.6f}")

                # Log parameters
                param_names = analyzer.config.get(
                    "parameter_names", [f"p{i}" for i in range(len(parameters))]
                )
                for i, (name, value) in enumerate(
                    zip(param_names, parameters, strict=False)
                ):
                    logger.info(f"✓ {name}: {value:.6f}")

                # Store result for this method
                method_result = {
                    "method": method,
                    "parameters": parameters,
                    "chi_squared": chi_squared,
                    "success": success,
                    "result_object": result_info,
                }
                all_results[method] = method_result

                # Track best result
                if chi_squared > 0 and chi_squared < best_chi_squared:
                    best_chi_squared = chi_squared
                    best_result = method_result

            except Exception as e:
                logger.warning(f"⚠️  {method.capitalize()} optimization failed: {e}")
                continue

        logger.info("")
        logger.info("=" * 50)
        logger.info("ROBUST OPTIMIZATION SUMMARY")
        logger.info("=" * 50)

        if not all_results:
            logger.error("❌ All robust optimization methods failed")
            return None

        # Log summary of all methods
        for method, result in all_results.items():
            logger.info(
                f"{method.capitalize():15s}: χ² = {result['chi_squared']:.6f}, "
                f"success = {result['success']}"
            )

        if best_result:
            logger.info("")
            logger.info(
                f"⭐ Best method: {best_result['method']} (χ² = {best_chi_squared:.6f})"
            )

        logger.info("=" * 50)

        # Return the best result with all_results attached
        return {
            "method": "robust",
            "parameters": best_result["parameters"],
            "chi_squared": best_result["chi_squared"],
            "success": best_result["success"],
            "result_object": best_result["result_object"],
            "all_robust_results": all_results,  # Include all method results
        }

    except Exception as e:
        logger.error(f"❌ Robust optimization failed: {e}")
        import traceback

        logger.debug(f"Full traceback: {traceback.format_exc()}")
        return None


def run_all_methods(analyzer, initial_params, phi_angles, c2_exp, output_dir=None):
    """
    Execute both classical and robust optimization methods.

    This function is called by --method all and runs ALL available methods:

    Classical Methods:
    - Nelder-Mead (always available)
    - Gurobi (if available and licensed)

    Robust Methods:
    - Robust-Wasserstein (Distributionally Robust Optimization)
    - Robust-Scenario (Bootstrap-based)
    - Robust-Ellipsoidal (Bounded uncertainty)

    Provides comprehensive analysis with both traditional and robust approaches,
    allowing comparison of optimization strategies and assessment of parameter
    reliability across different methodologies.

    Parameters
    ----------
    analyzer : HomodyneAnalysisCore
        Main analysis engine with loaded configuration
    initial_params : list
        Starting parameter values for optimization
    phi_angles : ndarray
        Angular coordinates for the scattering data
    c2_exp : ndarray
        Experimental correlation function data
    output_dir : Path, optional
        Directory for saving all results and comparison plots

    Returns
    -------
    dict
        Combined results dictionary with both classical and robust results
    """
    logger.info("Running all optimization methods...")
    logger.info("=" * 50)

    results = {}

    # Run classical optimization
    logger.info("PHASE 1: Classical Optimization")
    logger.info("-" * 30)
    classical_result = run_classical_optimization(
        analyzer, initial_params, phi_angles, c2_exp, output_dir
    )

    if classical_result:
        results["classical"] = classical_result
        logger.info("✓ Classical optimization phase completed")
    else:
        logger.warning("⚠️  Classical optimization phase failed")

    logger.info("")

    # Run robust optimization
    logger.info("PHASE 2: Robust Optimization")
    logger.info("-" * 30)
    robust_result = run_robust_optimization(
        analyzer, initial_params, phi_angles, c2_exp, output_dir
    )

    if robust_result:
        results["robust"] = robust_result
        logger.info("✓ Robust optimization phase completed")
    else:
        logger.warning("⚠️  Robust optimization phase failed")

    logger.info("")
    logger.info("=" * 50)
    logger.info("OPTIMIZATION SUMMARY")
    logger.info("=" * 50)

    # Summary comparison
    if "classical" in results and "robust" in results:
        classical_chi2 = results["classical"]["chi_squared"]
        robust_chi2 = results["robust"]["chi_squared"]

        logger.info(f"Classical chi-squared: {classical_chi2:.6f}")
        logger.info(f"Robust chi-squared:    {robust_chi2:.6f}")

        if classical_chi2 < robust_chi2:
            logger.info("⭐ Classical optimization achieved better fit")
        elif robust_chi2 < classical_chi2:
            logger.info("⭐ Robust optimization achieved better fit")
        else:
            logger.info("📊 Both methods achieved similar fit quality")

    elif "classical" in results:
        logger.info("⚠️  Only classical optimization succeeded")

    elif "robust" in results:
        logger.info("⚠️  Only robust optimization succeeded")

    else:
        logger.error("❌ Both optimization phases failed")

    logger.info("=" * 50)

    return results
