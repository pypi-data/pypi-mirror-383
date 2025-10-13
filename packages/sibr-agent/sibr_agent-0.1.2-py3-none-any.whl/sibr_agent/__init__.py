"""sibr-agent package.

Exports public classes for external use.
"""

from .base import Agent  # noqa: F401
from .google_auth import GoogleAuth  # noqa: F401
# Avoid importing Firestore integration at package import time to keep deps light.
