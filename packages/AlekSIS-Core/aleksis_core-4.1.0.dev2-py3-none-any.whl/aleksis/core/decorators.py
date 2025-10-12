from functools import wraps


def pwa_cache(view_func):
    """Add headers to a response so that the PWA will recognize it as cacheable."""

    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        # Ensure argument looks like a request.
        if not hasattr(request, "META"):
            raise TypeError(
                "pwa_cache didn't receive an HttpRequest. If you are "
                "decorating a classmethod, be sure to use @method_decorator."
            )
        response = view_func(request, *args, **kwargs)
        response.headers["PWA-Is-Cacheable"] = "true"
        response.headers["Access-Control-Expose-Headers"] = "PWA-Is-Cacheable"
        return response

    return _wrapped_view_func
