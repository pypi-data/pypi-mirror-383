"""
Django Electric - Django integration for Electric SQL real-time sync engine
"""

__version__ = "0.1.1"
__author__ = "Your Name"
__license__ = "Apache-2.0"

from .client import ElectricClient
from .sync import SyncManager, SyncShape
from .models import ElectricSyncMixin
from .managers import ElectricManager

__all__ = [
    "ElectricClient",
    "SyncManager",
    "SyncShape",
    "ElectricSyncMixin",
    "ElectricManager",
]


default_app_config = "django_electric.apps.DjangoElectricConfig"
