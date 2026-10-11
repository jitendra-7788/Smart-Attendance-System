"""
Custom middleware to prevent session creation for API endpoints
This ensures JWT tokens are used exclusively for API authentication
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.middleware import SessionMiddleware


class DisableSessionForAPIMiddleware(MiddlewareMixin):
    """
    Middleware to disable session creation for API endpoints.
    This prevents session cookie collisions when faculty and students
    log in from different tabs.
    """
    
    def process_request(self, request):
        # Disable session creation for API endpoints
        if request.path.startswith('/api/'):
            # Prevent session middleware from creating sessions for API requests
            # JWT tokens in Authorization header will be used instead
            # This ensures each tab/browser has its own authentication state
            request.session = type('MockSession', (), {
                'save': lambda self: None,
                'delete': lambda self: None,
                'flush': lambda self: None,
                'cycle_key': lambda self: None,
                'get': lambda self, key, default=None: default,
                'pop': lambda self, key, default=None: default,
                'setdefault': lambda self, key, value: value,
                '__contains__': lambda self, key: False,
                '__getitem__': lambda self, key: None,
                '__setitem__': lambda self, key, value: None,
                '__delitem__': lambda self, key: None,
                'keys': lambda self: [],
                'values': lambda self: [],
                'items': lambda self: [],
                'clear': lambda self: None,
                'modified': False,
                'accessed': False,
            })()
        
        return None

