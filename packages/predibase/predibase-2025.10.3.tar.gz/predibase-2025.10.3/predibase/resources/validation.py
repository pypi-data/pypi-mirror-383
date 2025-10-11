from pydantic import TypeAdapter


class ValidatedDict(dict):
    def __init__(self, kt: type, vt: type, *args, **kwargs):
        self._kt = kt
        self._vt = vt
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        key = TypeAdapter(self._kt).validate_python(key)
        value = TypeAdapter(self._vt).validate_python(value)
        super().__setitem__(key, value)
