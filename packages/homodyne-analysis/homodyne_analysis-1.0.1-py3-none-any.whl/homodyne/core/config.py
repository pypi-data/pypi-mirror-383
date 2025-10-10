"""
Configuration Management for Homodyne Scattering Analysis
=========================================================

Centralized configuration system for XPCS analysis under nonequilibrium conditions.
Provides JSON-based configuration management with validation, hierarchical parameter
organization, and performance optimization features.

Key Features:
- Hierarchical JSON configuration with validation
- Runtime parameter override capabilities
- Performance-optimized configuration access with caching
- Comprehensive logging system with rotation and formatting
- Physical parameter validation and bounds checking
- Angle filtering configuration for computational efficiency
- Test configuration management for different analysis scenarios

Configuration Structure:
- analyzer_parameters: Core physics parameters (q-vector, time steps, geometry)
- experimental_data: Data paths, file formats, and loading options
- analysis_settings: Mode selection (static vs laminar flow)
- optimization_config: Method settings, hyperparameters, angle filtering
- parameter_space: Physical bounds, priors, and parameter constraints
- performance_settings: Computational optimization flags

Authors: Wei Chen, Hongrui He
Institution: Argonne National Laboratory
"""

import gc
import json
import logging
import multiprocessing as mp
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any
from typing import NotRequired
from typing import TypedDict
from typing import cast

# Import security features
try:
    from .security_performance import ValidationError
    from .security_performance import secure_config_loader

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    ValidationError = ValueError  # Fallback

# Default parallelization setting - balance performance and resource usage
# Limit to 16 threads to avoid overwhelming system resources while providing
# substantial speedup for computational kernels
DEFAULT_NUM_THREADS = min(16, mp.cpu_count())

# Module-level logger for configuration-related messages
logger = logging.getLogger(__name__)


# TypedDict definitions for strong typing of configuration structures
class LoggingConfig(TypedDict, total=False):
    """Typed configuration for logging system."""

    log_to_file: bool
    log_to_console: bool
    log_filename: str
    level: str
    format: str
    rotation: dict[str, int | str]


class AngleRange(TypedDict):
    """Typed configuration for angle filtering ranges."""

    min_angle: float
    max_angle: float


class AngleFilteringConfig(TypedDict, total=False):
    """Typed configuration for angle filtering."""

    enabled: bool
    target_ranges: list[AngleRange]
    fallback_to_all_angles: bool


class OptimizationMethodConfig(TypedDict, total=False):
    """Typed configuration for optimization method parameters."""

    maxiter: int
    xatol: float
    fatol: float


class ClassicalOptimizationConfig(TypedDict, total=False):
    """Typed configuration for classical optimization methods."""

    methods: list[str]
    method_options: dict[str, OptimizationMethodConfig]


class OptimizationConfig(TypedDict, total=False):
    """Typed configuration for optimization settings."""

    angle_filtering: AngleFilteringConfig
    classical_optimization: ClassicalOptimizationConfig


class ParameterBound(TypedDict):
    """Typed configuration for parameter bounds."""

    name: str
    min: float
    max: float
    type: str  # "uniform" or "log-uniform"


class ParameterSpaceConfig(TypedDict, total=False):
    """Typed configuration for parameter space definition."""

    bounds: list[ParameterBound]


class InitialParametersConfig(TypedDict, total=False):
    """Typed configuration for initial parameter values."""

    values: list[float]
    parameter_names: list[str]
    active_parameters: NotRequired[list[str]]


class AnalysisSettings(TypedDict, total=False):
    """Typed configuration for analysis mode settings."""

    static_mode: bool
    static_submode: NotRequired[str]  # "isotropic" or "anisotropic"
    model_description: dict[str, str]


class ExperimentalDataConfig(TypedDict, total=False):
    """Typed configuration for experimental data paths."""

    data_folder_path: str
    data_file_name: str
    phi_angles_path: str
    phi_angles_file: str
    exchange_key: str
    cache_file_path: str
    cache_filename_template: str


def configure_logging(
    cfg: dict[str, Any] | None = None, *, level: Any = None, log_file: str | None = None
) -> logging.Logger:
    """
    Configure centralized logging system with hierarchy and handlers.

    This function sets up a complete logging infrastructure:
    - Creates a logger hierarchy (root + module logger)
    - Sets up RotatingFileHandler with size-based rotation
    - Optionally creates StreamHandler for console output
    - Applies consistent formatting and log levels

    Parameters
    ----------
    cfg : dict, optional
        Logging configuration dictionary with keys:
        - log_to_file: bool, enable file logging
        - log_to_console: bool, enable console logging
        - log_filename: str, log file path
        - level: str, logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        - format: str, log message format string
        - rotation: dict with 'max_bytes' and 'backup_count'
    level : Any, optional
        Logging level for backward compatibility (can be string or logging constant)
    log_file : str, optional
        Log file path for backward compatibility

    Returns
    -------
    logging.Logger
        Configured logger instance for reuse
    """
    # Handle backward compatibility with individual parameters
    if cfg is None:
        cfg = {}

    # Convert individual parameters to config dict for backward compatibility
    if level is not None:
        if isinstance(level, int):
            # Convert logging level constant to string
            level_names = {
                logging.DEBUG: "DEBUG",
                logging.INFO: "INFO",
                logging.WARNING: "WARNING",
                logging.ERROR: "ERROR",
                logging.CRITICAL: "CRITICAL",
            }
            cfg["level"] = level_names.get(level, "INFO")
        else:
            cfg["level"] = str(level)

    if log_file is not None:
        cfg["log_to_file"] = True
        cfg["log_filename"] = log_file

    # Set defaults for backward compatibility
    if "log_to_console" not in cfg:
        cfg["log_to_console"] = True
    # Clear any existing handlers to avoid conflicts
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Get or create module logger
    module_logger = logging.getLogger(__name__)
    for handler in module_logger.handlers[:]:
        module_logger.removeHandler(handler)

    # Parse configuration
    log_level = getattr(logging, cfg.get("level", "INFO").upper(), logging.INFO)
    format_str = cfg.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    formatter = logging.Formatter(format_str)

    # Set up root logger level
    root_logger.setLevel(log_level)
    module_logger.setLevel(log_level)

    # Suppress matplotlib font debug messages to reduce log noise
    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)

    handlers_created = []

    # File handler with rotation
    if cfg.get("log_to_file", False):
        filename = cfg.get("log_filename", "homodyne_analysis.log")
        rotation_config = cfg.get("rotation", {})
        max_bytes = rotation_config.get("max_bytes", 10 * 1024 * 1024)  # 10MB default
        backup_count = rotation_config.get("backup_count", 3)

        try:
            file_handler = RotatingFileHandler(
                filename=filename,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)

            # Add to both root and module logger
            root_logger.addHandler(file_handler)
            module_logger.addHandler(file_handler)
            handlers_created.append(
                f"RotatingFileHandler({filename}, {max_bytes // 1024 // 1024}MB, {
                    backup_count
                } backups)"
            )

        except OSError as e:
            logger.warning(f"Failed to create file handler: {e}")
            logger.info("Continuing with console logging only...")

    # Console handler
    if cfg.get("log_to_console", False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        # Add to both root and module logger
        root_logger.addHandler(console_handler)
        module_logger.addHandler(console_handler)
        handlers_created.append("StreamHandler(console)")

    # Prevent propagation to avoid duplicate messages
    module_logger.propagate = False

    if handlers_created:
        handler_list = ", ".join(handlers_created)
        logger.info(
            f"Logging configured: {handler_list} (level={cfg.get('level', 'INFO')})"
        )

        # Log initial message to verify setup
        module_logger.info(f"Logging system initialized: {handler_list}")
        module_logger.debug(f"Logger hierarchy: root -> {__name__}")
    else:
        logger.info("No logging handlers configured")

    return module_logger


class ConfigManager:
    """
    Centralized configuration manager for homodyne scattering analysis.

    This class orchestrates the entire configuration system for XPCS analysis,
    providing structured access to all analysis parameters with validation,
    caching, and runtime override capabilities.

    Core Responsibilities:
    - JSON configuration file loading with comprehensive error handling
    - Hierarchical parameter validation (physics, computation, file paths)
    - Performance-optimized configuration access through intelligent caching
    - Runtime configuration overrides for analysis mode switching
    - Logging system setup with rotation and appropriate formatting
    - Test configuration management for different experimental scenarios

    Configuration Hierarchy:
    - analyzer_parameters: Physics parameters (q-vector, time steps, gap size)
    - experimental_data: Data file paths, loading options, caching settings
    - analysis_settings: Mode selection (static/laminar flow), model descriptions
    - optimization_config: Method settings, angle filtering, hyperparameters
    - parameter_space: Physical parameter bounds, prior distributions
    - performance_settings: Parallelization, computational optimizations
    - validation_rules: Data quality checks and minimum requirements
    - advanced_settings: Fine-tuning options for specialized use cases

    Usage:
        config_manager = ConfigManager('my_config.json')
        is_static = config_manager.is_static_mode_enabled()
        angle_ranges = config_manager.get_target_angle_ranges()
    """

    def __init__(
        self,
        config_file: str = "homodyne_config.json",
        config: dict[str, Any] | None = None,
    ):
        """
        Initialize configuration manager.

        Parameters
        ----------
        config_file : str
            Path to JSON configuration file
        config : dict, optional
            Configuration dictionary (if provided, config_file is ignored)
        """
        self.config_file = config_file
        self.config: dict[str, Any] | None = None
        self._cached_values: dict[str, Any] = {}

        if config is not None:
            # Use provided config dictionary
            self.config = config
            # Don't validate provided config in constructor - let caller handle validation
            self.setup_logging()
        else:
            # Load from file and validate
            self.load_config()
            self.validate_config()
            self.setup_logging()

    def load_config(self, config_file: str | None = None) -> dict[str, Any] | None:
        """
        Load and parse JSON configuration file with comprehensive error handling and security validation.

        Implements performance-optimized loading with buffering, structure
        optimization for runtime access, security validation, and graceful fallback to default
        configuration if primary config fails.

        Security Features:
        - Input validation and sanitization
        - Path traversal prevention
        - Configuration structure validation
        - Parameter bounds checking

        Error Handling:
        - FileNotFoundError: Missing configuration file
        - JSONDecodeError: Malformed JSON syntax
        - ValidationError: Security validation failures
        - General exceptions: Unexpected loading issues

        Performance Optimizations:
        - 8KB buffering for efficient file I/O
        - Configuration structure caching for fast access
        - Timing instrumentation for performance monitoring
        """
        # Use provided config_file parameter or fall back to instance variable
        actual_config_file = (
            config_file if config_file is not None else self.config_file
        )

        with performance_monitor.time_function("config_loading"):
            try:
                if actual_config_file is None:
                    raise ValueError("Configuration file path cannot be None")

                config_path = Path(actual_config_file)
                if not config_path.exists():
                    raise FileNotFoundError(
                        f"Configuration file not found: {actual_config_file}"
                    )

                # Security-enhanced configuration loading
                if SECURITY_AVAILABLE:
                    try:
                        logger.debug("Loading configuration with security validation")
                        self.config = secure_config_loader(config_path)
                        logger.info(
                            f"Secure configuration loaded from: {actual_config_file}"
                        )
                    except ValidationError as e:
                        logger.warning(f"Security validation failed: {e}")
                        logger.info("Falling back to standard loading...")
                        # Fall back to standard loading
                        self._load_config_standard(config_path)
                else:
                    # Standard loading when security features unavailable
                    self._load_config_standard(config_path)

                # Optimize configuration structure for faster runtime access
                self._optimize_config_structure()

                # Display version information if available
                if isinstance(self.config, dict) and "metadata" in self.config:
                    version = self.config["metadata"].get("config_version", "Unknown")
                    logger.info(f"Configuration version: {version}")

            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.info("Using default configuration...")
                self.config = self._get_default_config()
            except FileNotFoundError as e:
                logger.error(f"Failed to load configuration: {e}")
                logger.info("Attempting to load default template...")
                try:
                    # Try to load a default template from the config directory
                    from homodyne.config import get_template_path

                    template_path = get_template_path("template")
                    with open(template_path, encoding="utf-8") as f:
                        self.config = json.load(f)
                    logger.info(
                        f"Loaded default template configuration from: {template_path}"
                    )
                except Exception as template_error:
                    logger.warning(f"Failed to load default template: {template_error}")
                    logger.info("Using built-in default configuration...")
                    self.config = self._get_default_config()
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                logger.exception("Full traceback for configuration loading failure:")
                logger.info("Using built-in default configuration...")
                self.config = self._get_default_config()

        return self.config

    def _load_config_standard(self, config_path: Path) -> None:
        """
        Standard configuration loading without security enhancements.
        """
        # Optimized JSON loading with memory pre-allocation hints
        with open(config_path, encoding="utf-8", buffering=8192) as f:
            raw_config = json.load(f)

        self.config = raw_config
        logger.info(f"Configuration loaded from: {self.config_file}")

    def _optimize_config_structure(self) -> None:
        """
        Pre-compute and cache frequently accessed configuration values.

        This optimization reduces repeated nested dictionary lookups during
        analysis runtime, particularly for values accessed in tight loops
        such as angle filtering settings and parameter bounds.

        Cached Values:
        - angle_filtering_enabled: Boolean flag for optimization filtering
        - target_angle_ranges: Pre-parsed angle ranges for filtering
        - static_mode: Analysis mode flag (static vs laminar flow)
        - parameter_bounds: Parameter constraints for validation
        - effective_param_count: Number of active parameters (3 or 7)
        """
        if not self.config:
            return

        # Initialize cache dictionary for performance-critical values (already
        # initialized in __init__)

        # Cache optimization config paths
        if "optimization_config" in self.config:
            opt_config = self.config["optimization_config"]
            self._cached_values["angle_filtering_enabled"] = opt_config.get(
                "angle_filtering", {}
            ).get("enabled", True)
            self._cached_values["target_angle_ranges"] = opt_config.get(
                "angle_filtering", {}
            ).get("target_ranges", [])

        # Cache analysis settings
        if "analysis_settings" in self.config:
            analysis = self.config["analysis_settings"]
            self._cached_values["static_mode"] = analysis.get("static_mode", False)

            # Cache static submode if static mode is enabled
            if self._cached_values["static_mode"]:
                raw_submode = analysis.get("static_submode", "anisotropic")
                if raw_submode is None:
                    submode = "anisotropic"
                else:
                    submode_str = str(raw_submode).lower().strip()
                    if submode_str in ["isotropic", "iso"]:
                        submode = "isotropic"
                    elif submode_str in ["anisotropic", "aniso"]:
                        submode = "anisotropic"
                    else:
                        submode = "anisotropic"
                self._cached_values["static_submode"] = submode
            else:
                self._cached_values["static_submode"] = None

        # Cache parameter bounds for faster access
        if "parameter_space" in self.config:
            bounds = self.config["parameter_space"].get("bounds", [])
            self._cached_values["parameter_bounds"] = bounds

        # Pre-compute effective parameter count
        self._cached_values["effective_param_count"] = (
            3 if self._cached_values.get("static_mode", False) else 7
        )

    def validate_config(self) -> bool:
        """
        Comprehensive validation of configuration parameters.

        Performs multi-level validation to ensure configuration integrity:

        Structural Validation:
        - Required sections presence (analyzer_parameters, experimental_data, etc.)
        - Configuration hierarchy completeness
        - Parameter type consistency

        Physical Parameter Validation:
        - Frame range consistency (start < end, sufficient frames)
        - Wavevector positivity and reasonable magnitude
        - Time step positivity
        - Gap size physical reasonableness

        Data Validation:
        - Minimum frame count requirements
        - Parameter bounds consistency
        - File path accessibility (optional)

        Raises
        ------
        ValueError
            Invalid configuration parameters or structure
        FileNotFoundError
            Missing required data files (if validation enabled)
        """
        if not self.config:
            return False

        # Check required sections
        required_sections = [
            "analyzer_parameters",
            "experimental_data",
            "optimization_config",
        ]
        missing = [s for s in required_sections if s not in self.config]
        if missing:
            return False

        # Validate frame range
        analyzer = self.config.get("analyzer_parameters", {})
        temporal = analyzer.get("temporal", {})
        start = temporal.get("start_frame", 1)
        end = temporal.get("end_frame", 100)

        if start >= end:
            return False

        # Check minimum frame count
        min_frames = (
            self.config.get("validation_rules", {})
            .get("frame_range", {})
            .get("minimum_frames", 10)
        )
        if end - start < min_frames:
            return False

        # Validate physical parameters
        try:
            self._validate_physical_parameters()
        except (ValueError, KeyError):
            return False

        logger.info(
            f"Configuration validated: frames {start}-{end} ({end - start + 1} frames)"
        )

        return True

    def validate_parameter_bounds(self, parameters: dict[str, float]) -> bool:
        """
        Validate that parameters are within the configured bounds.

        Parameters
        ----------
        parameters : dict[str, float]
            Dictionary of parameter names and values to validate

        Returns
        -------
        bool
            True if all parameters are within bounds, False otherwise
        """
        import numpy as np

        if not self.config:
            return False

        # Try multiple locations for parameter bounds (backwards compatibility)
        bounds = self.config.get("parameter_bounds", {}) or self.config.get(
            "optimization_config", {}
        ).get("parameter_bounds", {})

        if not bounds:
            # If no bounds configured, assume validation passes
            return True

        for param_name, param_value in parameters.items():
            # Check for NaN or Inf values
            if not np.isfinite(param_value):
                return False

            if param_name in bounds:
                min_val, max_val = bounds[param_name]
                if not (min_val <= param_value <= max_val):
                    return False

        return True

    def get_parameter(self, section: str, parameter: str, default: Any = None) -> Any:
        """
        Get a parameter value from a specific configuration section.

        Parameters
        ----------
        section : str
            Configuration section name
        parameter : str
            Parameter name within the section
        default : Any, optional
            Default value to return if parameter not found

        Returns
        -------
        Any
            Parameter value

        Raises
        ------
        KeyError
            If parameter not found and no default provided
        """
        if not self.config:
            if default is not None:
                return default
            raise KeyError("Configuration not loaded")

        if section not in self.config:
            if default is not None:
                return default
            raise KeyError(f"Section '{section}' not found in configuration")

        section_config = self.config[section]
        if parameter not in section_config:
            if default is not None:
                return default
            raise KeyError(f"Parameter '{parameter}' not found in section '{section}'")

        return section_config[parameter]

    def set_parameter(self, section: str, parameter: str, value: Any) -> None:
        """
        Set a parameter value in a specific configuration section.

        Parameters
        ----------
        section : str
            Configuration section name
        parameter : str
            Parameter name within the section
        value : Any
            Value to set for the parameter

        Raises
        ------
        KeyError
            If section not found in configuration
        """
        if not self.config:
            raise KeyError("Configuration not loaded")

        if section not in self.config:
            # Create section if it doesn't exist
            self.config[section] = {}

        self.config[section][parameter] = value

    def merge_configs(self, update_config: dict[str, Any]) -> dict[str, Any]:
        """
        Merge an update configuration with the current configuration.

        Parameters
        ----------
        update_config : dict[str, Any]
            Configuration dictionary to merge with current config

        Returns
        -------
        dict[str, Any]
            Merged configuration dictionary
        """
        if not self.config:
            return update_config.copy()

        # Deep merge configurations
        merged = self._deep_merge_dicts(self.config.copy(), update_config)
        return merged

    def save_config(self, file_path: str) -> None:
        """
        Save the current configuration to a JSON file.

        Parameters
        ----------
        file_path : str
            Path where the configuration file should be saved

        Raises
        ------
        ValueError
            If no configuration is loaded
        FileNotFoundError
            If the parent directory doesn't exist
        """
        if not self.config:
            raise ValueError("No configuration loaded to save")

        from pathlib import Path

        # Ensure parent directory exists
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save configuration with proper formatting
        with open(file_path, "w") as f:
            json.dump(self.config, f, indent=2, default=str)

    def _deep_merge_dicts(self, base: dict, update: dict) -> dict:
        """
        Recursively merge two dictionaries.

        Parameters
        ----------
        base : dict
            Base dictionary
        update : dict
            Dictionary to merge into base

        Returns
        -------
        dict
            Merged dictionary
        """
        result = base.copy()

        for key, value in update.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge_dicts(result[key], value)
            else:
                result[key] = value

        return result

    def _validate_physical_parameters(self) -> None:
        """
        Validate physical parameters for scientific and computational validity.

        Performs detailed validation of core physics parameters to ensure
        they fall within physically meaningful and computationally stable ranges.

        Parameter Checks:
        - Wavevector q: Must be positive, warns if outside typical XPCS range
        - Time step dt: Must be positive for temporal evolution
        - Gap size h: Must be positive for rheometer geometry

        Typical Parameter Ranges:
        - q-vector: 0.001-0.1 Å⁻¹ (typical XPCS range)
        - Time step: 0.01-10 s (depending on dynamics)
        - Gap size: μm-mm range (rheometer geometry)

        Raises
        ------
        ValueError
            Invalid parameter values that would cause computation failure
        """
        if self.config is None or "analyzer_parameters" not in self.config:
            raise ValueError(
                "Configuration or 'analyzer_parameters' section is missing."
            )

        params = self.config["analyzer_parameters"]

        # Wavevector validation
        q = params.get("wavevector_q", 0.0054)
        if q <= 0:
            raise ValueError(f"Wavevector must be positive: {q}")
        if q > 1.0:
            logger.warning(f"Large wavevector: {q} Å⁻¹ (typical: 0.001-0.1)")

        # Time step validation
        dt = params.get("dt", 0.1)
        if dt <= 0:
            raise ValueError(f"Time step must be positive: {dt}")

        # Gap size validation
        h = params.get("stator_rotor_gap", 2000000)
        if h <= 0:
            raise ValueError(f"Gap size must be positive: {h}")

    def setup_logging(self) -> logging.Logger | None:
        """Configure logging based on configuration using centralized configure_logging()."""
        if self.config is None:
            logger.warning("Configuration is None, skipping logging setup.")
            return None

        log_config = self.config.get("logging", {})

        # Skip logging setup if neither file nor console logging is enabled
        if not log_config.get("log_to_file", False) and not log_config.get(
            "log_to_console", False
        ):
            return None

        # Use the centralized configure_logging function
        try:
            configured_logger = configure_logging(log_config)
            return configured_logger
        except Exception as e:
            logger.warning(f"Failed to configure logging: {e}")
            logger.exception("Full traceback for logging configuration failure:")
            logger.info("Continuing without logging...")
            return None

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get nested configuration value.

        Parameters
        ----------
        *keys : str
            Sequence of nested keys
        default : any
            Default value if key not found

        Returns
        -------
        Configuration value or default
        """
        try:
            value = self.config
            for key in keys:
                if value is None or not isinstance(value, dict):
                    return default
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def get_angle_filtering_config(self) -> dict[str, Any]:
        """
        Get angle filtering configuration with defaults.

        Returns
        -------
        dict
            Angle filtering configuration including:
            - enabled: bool, whether angle filtering is enabled
            - target_ranges: list of dicts with min_angle and max_angle
            - fallback_to_all_angles: bool, whether to use all angles if no targets found
        """
        angle_filtering = self.get("optimization_config", "angle_filtering", default={})

        # Ensure angle_filtering is a dictionary for unpacking
        if not isinstance(angle_filtering, dict):
            angle_filtering = {}

        # Provide sensible defaults if configuration is missing or incomplete
        default_config = {
            "enabled": True,
            "target_ranges": [
                {"min_angle": -10.0, "max_angle": 10.0},
                {"min_angle": 170.0, "max_angle": 190.0},
            ],
            "fallback_to_all_angles": True,
        }

        # Merge with defaults
        result = {**default_config, **angle_filtering}

        # Validate target_ranges structure
        if "target_ranges" in result:
            valid_ranges = []
            for range_config in result["target_ranges"]:
                if (
                    isinstance(range_config, dict)
                    and "min_angle" in range_config
                    and "max_angle" in range_config
                ):
                    valid_ranges.append(
                        {
                            "min_angle": float(range_config["min_angle"]),
                            "max_angle": float(range_config["max_angle"]),
                        }
                    )
                else:
                    logger.warning(f"Invalid angle range configuration: {range_config}")
            result["target_ranges"] = valid_ranges

        return result

    def is_angle_filtering_enabled(self) -> bool:
        """
        Check if angle filtering is enabled in configuration.

        Automatically returns False for static isotropic mode, regardless of
        configuration setting.

        Returns
        -------
        bool
            True if angle filtering should be used, False otherwise
        """
        # Always disable angle filtering for static isotropic mode
        if self.is_static_isotropic_enabled():
            # Warn if user explicitly enabled angle filtering but it's ignored
            explicit_enabled = self.get_angle_filtering_config().get("enabled", True)
            if explicit_enabled:
                logger.debug(
                    "Angle filtering disabled for static isotropic mode "
                    "(ignoring configuration setting)"
                )
            return False

        return bool(self.get_angle_filtering_config().get("enabled", True))

    def get_target_angle_ranges(self) -> list[tuple[float, float]]:
        """
        Get list of target angle ranges for optimization.

        Returns
        -------
        list of tuple
            List of (min_angle, max_angle) tuples in degrees
        """
        config = self.get_angle_filtering_config()
        ranges = config.get("target_ranges", [])

        return [(r["min_angle"], r["max_angle"]) for r in ranges]

    def should_fallback_to_all_angles(self) -> bool:
        """
        Check if system should fallback to all angles when no targets found.

        Returns
        -------
        bool
            True if should fallback to all angles, False to raise error
        """
        return bool(
            self.get_angle_filtering_config().get("fallback_to_all_angles", True)
        )

    def is_static_mode_enabled(self) -> bool:
        """
        Check if static mode is enabled in configuration.

        Returns
        -------
        bool
            True if static mode is enabled, False otherwise
        """
        # Use cached value for performance
        if hasattr(self, "_cached_values") and "static_mode" in self._cached_values:
            return bool(self._cached_values["static_mode"])

        result = self.get("analysis_settings", "static_mode", default=False)
        return bool(result)

    def get_static_submode(self) -> str | None:
        """
        Get the static sub-mode for analysis.

        Returns
        -------
        str | None
            "isotropic", "anisotropic", or None if static mode is disabled
        """
        # Return None if static mode is not enabled
        if not self.is_static_mode_enabled():
            return None

        # Use cached value for performance
        if hasattr(self, "_cached_values") and "static_submode" in self._cached_values:
            cached_value = self._cached_values["static_submode"]
            return str(cached_value) if cached_value is not None else None

        # Get submode from configuration (case-insensitive)
        raw_submode = self.get(
            "analysis_settings", "static_submode", default="anisotropic"
        )
        if raw_submode is None:
            submode = "anisotropic"  # Default for backward compatibility
        else:
            submode_str = str(raw_submode).lower().strip()
            if submode_str in ["isotropic", "iso"]:
                submode = "isotropic"
            elif submode_str in ["anisotropic", "aniso"]:
                submode = "anisotropic"
            else:
                logger.warning(
                    f"Invalid static_submode '{raw_submode}', defaulting to 'anisotropic'"
                )
                submode = "anisotropic"

        return submode

    def is_static_isotropic_enabled(self) -> bool:
        """
        Check if static isotropic mode is enabled.

        Returns
        -------
        bool
            True if analysis mode is static isotropic, False otherwise
        """
        return (
            self.is_static_mode_enabled() and self.get_static_submode() == "isotropic"
        )

    def is_static_anisotropic_enabled(self) -> bool:
        """
        Check if static anisotropic mode is enabled.

        Returns
        -------
        bool
            True if analysis mode is static anisotropic, False otherwise
        """
        return (
            self.is_static_mode_enabled() and self.get_static_submode() == "anisotropic"
        )

    def get_analysis_mode(self) -> str:
        """
        Get the current analysis mode.

        Returns
        -------
        str
            "static_isotropic", "static_anisotropic", or "laminar_flow"
        """
        if not self.is_static_mode_enabled():
            return "laminar_flow"

        submode = self.get_static_submode()
        if submode == "isotropic":
            return "static_isotropic"
        return "static_anisotropic"

    def get_active_parameters(self) -> list[str]:
        """
        Get list of active parameters from configuration.

        Returns
        -------
        list[str]
            List of parameter names to be optimized and displayed in plots.
            Falls back to all parameters if not specified in configuration.
        """
        initial_params = self.get("initial_parameters", default={})
        active_params = cast("list[str]", initial_params.get("active_parameters", []))

        # If no active_parameters specified, use all parameter names
        if not active_params:
            param_names = cast("list[str]", initial_params.get("parameter_names", []))
            if param_names:
                active_params = param_names
            else:
                # Ultimate fallback to standard parameter names
                active_params = [
                    "D0",
                    "alpha",
                    "D_offset",
                    "gamma_dot_t0",
                    "beta",
                    "gamma_dot_t_offset",
                    "phi0",
                ]

        return active_params

    def get_effective_parameter_count(self) -> int:
        """
        Get the effective number of model parameters based on active_parameters configuration.

        Returns
        -------
        int
            Number of parameters used in the analysis based on active_parameters.
            Falls back to mode-based logic if active_parameters not specified:
            - Static mode: 3 (only diffusion parameters)
            - Laminar flow mode: 7 (all parameters)
        """
        # Use cached value for performance
        if (
            hasattr(self, "_cached_values")
            and "effective_param_count" in self._cached_values
        ):
            return int(self._cached_values["effective_param_count"])

        # Get active parameters from configuration
        active_params = self.get_active_parameters()

        # Use active_parameters if specified, otherwise fall back to mode-based
        # logic
        if active_params:
            count = len(active_params)
        else:
            count = 3 if self.is_static_mode_enabled() else 7

        # Cache the result for performance
        if not hasattr(self, "_cached_values"):
            self._cached_values = {}
        self._cached_values["effective_param_count"] = count

        return count

    def list_available_templates(self) -> list[str]:
        """
        List all available configuration templates.

        Returns
        -------
        list[str]
            List of available template names
        """
        from homodyne.config import TEMPLATE_FILES

        return list(TEMPLATE_FILES.keys())

    def load_template(self, template_name: str) -> dict[str, Any]:
        """
        Load a configuration template by name.

        Parameters
        ----------
        template_name : str
            Name of the template to load

        Returns
        -------
        dict[str, Any]
            Template configuration dictionary

        Raises
        ------
        ValueError
            If template name is not found
        FileNotFoundError
            If template file doesn't exist
        """
        from homodyne.config import get_template_path

        try:
            template_path = get_template_path(template_name)
            with open(template_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load template '{template_name}': {e}")

    def resolve_environment_variables(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Resolve environment variables in configuration.

        Parameters
        ----------
        config : dict[str, Any]
            Configuration dictionary that may contain environment variable references

        Returns
        -------
        dict[str, Any]
            Configuration with environment variables substituted
        """
        import copy
        import os
        import re

        def substitute_env_vars(obj):
            if isinstance(obj, str):
                # Replace ${VAR_NAME} or $VAR_NAME patterns
                pattern = r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)"

                def replacer(match):
                    var_name = match.group(1) or match.group(2)
                    return os.environ.get(var_name, match.group(0))

                return re.sub(pattern, replacer, obj)
            if isinstance(obj, dict):
                return {key: substitute_env_vars(value) for key, value in obj.items()}
            if isinstance(obj, list):
                return [substitute_env_vars(item) for item in obj]
            return obj

        return substitute_env_vars(copy.deepcopy(config))

    def create_backup(self) -> dict[str, Any]:
        """
        Create a backup of the current configuration.

        Returns
        -------
        dict[str, Any]
            Deep copy of the current configuration

        Raises
        ------
        ValueError
            If no configuration is loaded
        """
        if not self.config:
            raise ValueError("No configuration loaded to backup")

        import copy

        return copy.deepcopy(self.config)

    def restore_from_backup(self, backup: dict[str, Any]) -> None:
        """
        Restore configuration from a backup.

        Parameters
        ----------
        backup : dict[str, Any]
            Configuration backup to restore
        """
        import copy

        self.config = copy.deepcopy(backup)

    def get_config_differences(self, other_config: dict[str, Any]) -> dict[str, Any]:
        """
        Get differences between current configuration and another configuration.

        Parameters
        ----------
        other_config : dict[str, Any]
            Configuration to compare against

        Returns
        -------
        dict[str, Any]
            Dictionary containing differences
        """
        if not self.config:
            return {"error": "No configuration loaded"}

        def find_differences(config1, config2, path=""):
            differences = {}

            # Check all keys in config1
            for key in config1:
                current_path = f"{path}.{key}" if path else key

                if key not in config2:
                    differences[key] = {"missing_in_other": config1[key]}
                elif isinstance(config1[key], dict) and isinstance(config2[key], dict):
                    nested_diff = find_differences(
                        config1[key], config2[key], current_path
                    )
                    if nested_diff:
                        differences[key] = nested_diff
                elif config1[key] != config2[key]:
                    differences[key] = {"current": config1[key], "other": config2[key]}

            # Check for keys only in config2
            for key in config2:
                if key not in config1:
                    differences[key] = {"missing_in_current": config2[key]}

            return differences

        return find_differences(self.config, other_config)

    def get_analysis_settings(self) -> dict[str, Any]:
        """
        Get analysis settings with defaults.

        Returns
        -------
        dict[str, Any]
            Analysis settings including static_mode flag and descriptions
        """
        analysis_settings = self.get("analysis_settings", default={})

        # Ensure analysis_settings is a dictionary for type safety
        if not isinstance(analysis_settings, dict):
            analysis_settings = {}

        # Provide sensible defaults
        default_settings = {
            "static_mode": False,
            "model_description": {
                "static_case": (
                    "g₁(t₁,t₂) = exp(-q² ∫ᵗ²ᵗ¹ D(t)dt) = g₁_diff(t₁,t₂), g₂(t₁,t₂) = [g₁(t₁,t₂)]²"
                ),
                "laminar_flow_case": (
                    "g₁(t₁,t₂) = g₁_diff(t₁,t₂) × g₁_shear(t₁,t₂) where g₁_shear = [sinc(Φ)]² and Φ = (1/2π)qL cos(φ₀-φ) ∫|t₂-t₁| γ̇(t')dt'"
                ),
            },
        }

        # Merge with defaults
        result = {**default_settings, **analysis_settings}
        return result

    def _get_default_config(self) -> dict[str, Any]:
        """Generate minimal default configuration."""
        return {
            "metadata": {
                "config_version": "5.1-default",
                "description": "Emergency fallback configuration",
            },
            "analyzer_parameters": {
                "temporal": {
                    "dt": 0.1,
                    "start_frame": 1001,
                    "end_frame": 2000,
                },
                "scattering": {"wavevector_q": 0.0054},
                "geometry": {"stator_rotor_gap": 2000000},
                "computational": {
                    "num_threads": DEFAULT_NUM_THREADS,
                    "auto_detect_cores": False,
                    "max_threads_limit": 128,
                },
            },
            "experimental_data": {
                "data_folder_path": "./data/C020/",
                "data_file_name": "default_data.hdf",
                "phi_angles_path": "./data/C020/",
                "phi_angles_file": "phi_list.txt",
                "exchange_key": "exchange",
                "cache_file_path": ".",
                "cache_filename_template": (
                    "cached_c2_frames_{start_frame}_{end_frame}.npz"
                ),
            },
            "analysis_settings": {
                "static_mode": False,
                "model_description": {
                    "static_case": (
                        "g₁(t₁,t₂) = exp(-q² ∫ᵗ²ᵗ¹ D(t)dt) = g₁_diff(t₁,t₂), g₂(t₁,t₂) = [g₁(t₁,t₂)]²"
                    ),
                    "laminar_flow_case": (
                        "g₁(t₁,t₂) = g₁_diff(t₁,t₂) × g₁_shear(t₁,t₂) where g₁_shear = [sinc(Φ)]² and Φ = (1/2π)qL cos(φ₀-φ) ∫|t₂-t₁| γ̇(t')dt'"
                    ),
                },
            },
            "initial_parameters": {
                "values": [1324.1, -0.014, -0.674361, 0.003, -0.909, 0.0, 0.0],
                "parameter_names": [
                    "D0",
                    "alpha",
                    "D_offset",
                    "gamma_dot_t0",
                    "beta",
                    "gamma_dot_t_offset",
                    "phi0",
                ],
            },
            "optimization_config": {
                "angle_filtering": {
                    "enabled": True,
                    "target_ranges": [
                        {"min_angle": -10.0, "max_angle": 10.0},
                        {"min_angle": 170.0, "max_angle": 190.0},
                    ],
                    "fallback_to_all_angles": True,
                },
                "classical_optimization": {
                    "methods": ["Nelder-Mead"],
                    "method_options": {
                        "Nelder-Mead": {
                            "maxiter": 5000,
                            "xatol": 1e-8,
                            "fatol": 1e-8,
                        }
                    },
                },
            },
            "parameter_space": {
                "bounds": [
                    {
                        "name": "D0",
                        "min": 1.0,
                        "max": 1e6,
                        "type": "Normal",
                    },
                    {
                        "name": "alpha",
                        "min": -2.0,
                        "max": 2.0,
                        "type": "Normal",
                    },
                    {
                        "name": "D_offset",
                        "min": -100,
                        "max": 100,
                        "type": "Normal",
                    },
                    {
                        "name": "gamma_dot_t0",
                        "min": 1e-6,
                        "max": 1.0,
                        "type": "Normal",
                    },
                    {
                        "name": "beta",
                        "min": -2.0,
                        "max": 2.0,
                        "type": "Normal",
                    },
                    {
                        "name": "gamma_dot_t_offset",
                        "min": -1e-2,
                        "max": 1e-2,
                        "type": "Normal",
                    },
                    {
                        "name": "phi0",
                        "min": -10.0,
                        "max": 10.0,
                        "type": "Normal",
                    },
                ]
            },
            "validation_rules": {"frame_range": {"minimum_frames": 10}},
            "performance_settings": {
                "parallel_execution": True,
                "use_threading": True,
                "optimization_counter_log_frequency": 100,
            },
            "advanced_settings": {
                "data_loading": {
                    "use_diagonal_correction": True,
                    "vectorized_diagonal_fix": True,
                },
                "chi_squared_calculation": {
                    "_scaling_optimization_note": "Scaling optimization is always enabled: g₂ = offset + contrast × g₁",
                    "uncertainty_estimation_factor": 0.1,
                    "minimum_sigma": 1e-10,
                    "validity_check": {
                        "check_positive_D0": True,
                        "check_positive_gamma_dot_t0": True,
                        "check_positive_time_dependent": True,
                        "check_parameter_bounds": True,
                    },
                },
            },
            "test_configurations": {
                "production": {
                    "description": "Standard production configuration",
                    "classical_methods": ["Nelder-Mead"],
                    "bo_n_calls": 20,
                }
            },
        }


class PerformanceMonitor:
    """
    Performance monitoring and profiling utilities.

    Provides lightweight profiling and memory monitoring
    for optimization of computational kernels.
    """

    def __init__(self) -> None:
        self.timings: dict[str, list[float]] = {}
        self.memory_usage: dict[str, float] = {}

    def __call__(self, operation_name: str) -> "PerformanceMonitor._TimingContext":
        """
        Make PerformanceMonitor callable as a context manager.

        Parameters
        ----------
        operation_name : str
            Name of the operation being monitored

        Returns
        -------
        _TimingContext
            Context manager for timing the operation
        """
        return self.time_function(operation_name)

    def start(
        self, operation_name: str = "default_operation"
    ) -> "PerformanceMonitor._TimingContext":
        """
        Start monitoring an operation.

        Parameters
        ----------
        operation_name : str, optional
            Name of the operation being monitored

        Returns
        -------
        _TimingContext
            Context manager for timing the operation
        """
        return self.time_function(operation_name)

    def time_function(self, func_name: str) -> "PerformanceMonitor._TimingContext":
        """
        Context manager for timing function execution.

        Parameters
        ----------
        func_name : str
            Name of function being timed

        Usage
        -----
        with monitor.time_function("my_function"):
            # function code here
            pass
        """
        return self._TimingContext(self, func_name)

    class _TimingContext:
        def __init__(self, monitor: "PerformanceMonitor", func_name: str) -> None:
            self.monitor = monitor
            self.func_name = func_name
            self.start_time: float | None = None

        def __enter__(self) -> "PerformanceMonitor._TimingContext":
            gc.collect()  # Clean memory before timing
            self.start_time = time.perf_counter()
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            # Suppress unused parameter warnings
            _ = exc_type, exc_val, exc_tb

            if self.start_time is not None:
                elapsed = time.perf_counter() - self.start_time
                if self.func_name not in self.monitor.timings:
                    self.monitor.timings[self.func_name] = []
                self.monitor.timings[self.func_name].append(elapsed)

    def get_timing_summary(self) -> dict[str, dict[str, float]]:
        """Get summary statistics for all timed functions."""
        summary = {}
        for func_name, times in self.timings.items():
            summary[func_name] = {
                "mean": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "total": sum(times),
                "calls": len(times),
            }
        return summary

    def reset_timings(self) -> None:
        """Clear all timing data."""
        self.timings.clear()
        self.memory_usage.clear()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
