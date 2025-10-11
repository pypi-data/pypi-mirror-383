from typing import Optional

# SmoothIntegration Python bindings
# API docs at http://smooth-integration.com/docs
# Authors:
# Thimo Visser <thimo@smooth-integration.com>

client_id: Optional[str] = None
client_secret: Optional[str] = None

from . import _http, companies, connections, data, exact, exceptions, quickbooks, zohobooks, request
