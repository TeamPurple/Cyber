# based on caching decorator from http://code.activestate.com/recipes/577479-simple-caching-decorator/

from functools import wraps

def cache():
    """Memoizing cache decorator.

    Arguments to the cached function must be hashable.
    """

    def decorating_function(user_function,
                tuple=tuple, sorted=sorted, len=len, KeyError=KeyError):

        cache = dict()
        kwd_mark = object()             # separates positional and keyword args

        @wraps(user_function)
        def wrapper(*args, **kwds):
            key = args
            if kwds:
                key += (kwd_mark,) + tuple(sorted(kwds.items()))
            try:
                result = cache[key]
            except KeyError:
                result = user_function(*args, **kwds)
                cache[key] = result
            return result

        def cache_clear():
            """Clear the cache and cache statistics"""
            cache.clear()

        wrapper.cache_clear = cache_clear
        return wrapper

    return decorating_function
