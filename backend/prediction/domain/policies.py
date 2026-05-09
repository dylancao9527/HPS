from importlib import import_module
from importlib.util import find_spec


_EXPORTS_BY_MODULE = {
    ".run_snapshot_policy": ["build_prediction_run_snapshot"],
    ".risk_policy": ["resolve_inference_bp_meds"],
    ".trend_policy": ["fuse_risk_with_trend", "summarize_forecast_trend"],
}

_AVAILABLE_EXPORTS = {
    module_name: names
    for module_name, names in _EXPORTS_BY_MODULE.items()
    if find_spec(f"{__package__}{module_name}") is not None
}

__all__ = [
    name for names in _AVAILABLE_EXPORTS.values() for name in names
]


def __getattr__(name: str):
    for module_name, names in _AVAILABLE_EXPORTS.items():
        if name not in names:
            continue
        module = import_module(module_name, __package__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(name)
