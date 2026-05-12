from functools import wraps
from django.core.cache import cache
from rest_framework.response import Response

def custom_cache_decorator(timeout):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            query_string = request.META.get('QUERY_STRING', '')
            cache_key = f"docs_cache_{request.path}?{query_string}"
            
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)

            response = view_func(self, request, *args, **kwargs)
            
            if response.status_code == 200:
                cache.set(cache_key, response.data, timeout)
                
            return response
        return _wrapped_view
    return decorator