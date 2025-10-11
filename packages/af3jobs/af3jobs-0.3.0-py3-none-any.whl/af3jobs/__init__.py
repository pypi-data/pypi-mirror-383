from importlib.metadata import version, PackageNotFoundError

from .server_jobs import Job as ServerJob
from .standalone_jobs import Job

try:
    __version__ = version("af3jobs")
except PackageNotFoundError:
    __version__ = "0.3.0-dev"

__all__ = ["ServerJob", "Job", "__version__"]
