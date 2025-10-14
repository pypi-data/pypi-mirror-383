from hyperx.templatetags.hyperx import *
import importlib, pkgutil, logging
_logger = logging.getLogger("hyperx_elements")

__all__ = []
failure = []
for module in pkgutil.iter_modules(__path__):
    try:
        importlib.import_module(f"{__name__}.{module.name}")
        __all__.append(module.name)
        _logger.debug(f"[HyperX Elements] Loaded: {module.name}")
    except Exception as e:
        failure.append(module.name)
        _logger.warning(f"[HyperX Elements] Failed to load {module.name}: {e}")

_logger.info(
    f"[HyperX Elements] {len(__all__)} modules registered, "
    f"{len(failure)} failed → {__all__}"
)
