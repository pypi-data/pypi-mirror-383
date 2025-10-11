from __future__ import annotations

from pathlib import Path

# Is set during `onbuild` if `pip install pipefunc` is used
__version__ = "0.87.1"

if not __version__:
    try:
        import versioningit
    except ImportError:  # pragma: no cover
        import importlib.metadata

        __version__ = importlib.metadata.version("pipefunc")
    else:
        PROJECT_DIR = Path(__file__).parent.parent
        __version__ = versioningit.get_version(project_dir=PROJECT_DIR)
