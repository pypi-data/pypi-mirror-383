from axiomtradeapi._client import AxiomTradeClient
from axiomtradeapi.auth.login import AxiomAuth

# Version
__version__ = "1.0.3"

# New client import (enhanced with PumpPortal trading)
try:
    from axiomtradeapi.client import AxiomTradeClient as EnhancedAxiomTradeClient, quick_login_and_get_trending, get_trending_with_token
    _has_enhanced_client = True
except ImportError:
    EnhancedAxiomTradeClient = None
    quick_login_and_get_trending = None
    get_trending_with_token = None
    _has_enhanced_client = False

__all__ = ['AxiomTradeClient', 'AxiomAuth', '__version__']

if _has_enhanced_client:
    __all__.extend(['EnhancedAxiomTradeClient', 'quick_login_and_get_trending', 'get_trending_with_token'])