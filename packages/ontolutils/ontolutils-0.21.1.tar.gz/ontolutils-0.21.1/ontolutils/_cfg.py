from typing import Dict

CONFIG = {
    'blank_id_generator': None,
    'show_lang_in_str': True
}
_VALIDATORS = {
    'blank_id_generator': lambda x: callable(x) or x is None,
    'show_lang_in_str': lambda x: isinstance(x, bool) or x is None,
}


class set_config:
    """Set the configuration parameters."""

    def __init__(self, **kwargs):
        self.old = {}
        for k, v in kwargs.items():
            if k in _VALIDATORS and not _VALIDATORS[k](v):
                raise ValueError(f'Config parameter "{k}" has invalid value: "{v}"')
            if k not in CONFIG:
                raise KeyError(f'Not a configuration key: "{k}"')
            self.old[k] = CONFIG[k]
        self._update(kwargs)

    def __enter__(self):
        return

    def __exit__(self, *args, **kwargs):
        self._update(self.old)

    def _update(self, options_dict: Dict):
        CONFIG.update(options_dict)


def get_config(key=None):
    """Return the configuration parameters."""
    if key is None:
        return CONFIG
    return CONFIG[key]
