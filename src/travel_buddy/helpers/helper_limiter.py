"""
Sets up rate limiting for the application.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address, default_limits=["3/second"], strategy="moving-window"
)
