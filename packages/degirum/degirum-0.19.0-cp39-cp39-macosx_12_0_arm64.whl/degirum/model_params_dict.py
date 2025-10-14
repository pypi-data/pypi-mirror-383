#
# model_params_dict.py - DeGirum Python SDK: _ModelParamsDict helper class
# Copyright DeGirum Corp. 2025
#
# Implements a helper for dot-access to a dict in model parameters
#
from typing import Any, Dict


class _ModelParamsDict:
    """
    Helper to provide dot-notation access for a dict in _model_parameters.
    Mutation happens through the ModelParams setter and marks dirty flag.
    """
    __slots__ = ("_mparams", "_name")

    def __init__(self, model_params, dict_name: str):
        object.__setattr__(self, "_mparams", model_params)
        object.__setattr__(self, "_name", dict_name)

    def _cur(self) -> Dict[str, Any]:
        """Read-only snapshot of current state (do not expose live reference)."""
        d = getattr(self._mparams, self._name, None)
        if d is None:
            return {}
        if not isinstance(d, dict):
            raise TypeError(f"{self._name} must be a dict")
        return dict(d)  # return a copy to prevent accidental external mutation

    def _commit(self, mutate):
        # Always write back through ModelParams. Its getter may return a copy,
        # so in-place mutation of that object would be lost unless we reassign.
        base = getattr(self._mparams, self._name, None)
        if base is None:
            base = {}
        else:
            if not isinstance(base, dict):
                raise TypeError(f"{self._name} must be a dict")
            base = dict(base)  # work on a fresh copy
        mutate(base)
        setattr(self._mparams, self._name, base)
        setattr(self._mparams, "dirty", True)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._cur()!r})"

    def __eq__(self, other):
        """Compare for equality with another _ModelParamsDict or a standard dict."""
        if isinstance(other, _ModelParamsDict):
            return self._cur() == other._cur()
        if isinstance(other, dict):
            return self._cur() == other
        return NotImplemented

    # dot access
    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):  # Block dunder names
            raise AttributeError(name)
        d = self._cur()
        if name in d:
            return d[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in type(self).__slots__:  # forbid touching slot attrs
            raise AttributeError(f"{name!r} is read-only")
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(f"Refusing to set reserved attribute {name!r}")
        self._commit(lambda d: d.__setitem__(name, value))

    # [] access
    def __getitem__(self, key):
        return self._cur()[key]

    def __setitem__(self, key, value):
        self._commit(lambda d: d.__setitem__(key, value))

    def __delitem__(self, key):
        self._commit(lambda d: d.__delitem__(key))

    def __contains__(self, key):
        return key in self._cur()

    def get(self, key, default=None):
        return self._cur().get(key, default)

    def keys(self):
        return self._cur().keys()

    def items(self):
        return self._cur().items()

    def values(self):
        return self._cur().values()
