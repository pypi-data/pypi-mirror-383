from .hook import set_hook as set_hook
from .load import load_hud
from .logging import internal_logger as internal_logger
from .standby_mode import activate_worker as activate
from .standby_mode import enter_standby_mode as standby
from .version import version as __version__
from .worker.worker import init_hud_thread as init

load_hud()

del load_hud
del internal_logger  # Can we just remove the import in the first place?

__all__ = ["__version__", "set_hook", "init", "standby", "activate"]
