from functools import wraps
from django.core.cache import cache
from rest_framework.response import Response
import hashlib

def custom_cache_decorator(timeout=60):
    
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_instance, request, *args, **kwargs):
            query_string = request.META.get('QUERY_STRING', '')

            # we can cahnge the caching mechanisem if we want for later
            raw_key = f"{request.path}:{query_string}"
            cache_key = f"docs_list_{hashlib.md5(raw_key.encode('utf-8')).hexdigest()}"
            
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
            response = view_func(view_instance, request, *args, **kwargs)
            if response.status_code == 200:
                cache.set(cache_key, response.data, timeout)
            return response
        return _wrapped_view
    return decorator