# src/ntp_client_facade/__init__.py

# This makes the main class available directly from the package
# So users can do: from ntp_client_facade import TimeBrokerFacade
# Instead of: from ntp_client_facade.facade import TimeBrokerFacade

from .facade import TimeBrokerFacade