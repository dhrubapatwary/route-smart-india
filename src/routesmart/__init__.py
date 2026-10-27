"""RouteSmart India: explainable, risk-aware multimodal travel recommendations.

Importing the package installs the redacting log handler on the ``routesmart``
logger, so no ``routesmart.*`` record can reach an unredacted handler, even
before ``configure_logging()`` is called (see ``docs/LOGGING.md``).
"""

from routesmart.log import ensure_redacting_handler

ensure_redacting_handler()
