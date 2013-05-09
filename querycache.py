import time
import threading


def cache_results(timeout=5 * 60):
    """
    Decorator to specify that a Query class should have its results cached.
    """

    def decorator(queryclass):
        queryclass.cache_timeout = timeout
        return queryclass

    return decorator


class QueryCache(object):
    """
    Execute queries through the QueryCache to ensure that the
    query's results are cached.
    """

    _shared_state = {
        'cached_queries': {},
        'lock': threading.Lock()
    }

    def __init__(self):
        self.__dict__ = self._shared_state

    def reset(self):
        with self.lock:
            self.cached_queries = {}

    def execute(self, queryclass, *args, **kwargs):
        if hasattr(queryclass, 'cache_timeout'):
            query_id = '.'.join([queryclass.__name__] + [str(a) for a in args])
            with self.lock:
                query = self.cached_queries.get(query_id)
                if not query:
                    query = queryclass()
                    query.last_update = 0
                    self.cached_queries[query_id] = query
                curr_time = time.time()
                if curr_time - query.last_update > queryclass.cache_timeout:
                    query.execute(*args, **kwargs)
                    query.last_update = curr_time
        else:
            query = queryclass()
            query.execute(*args, **kwargs)
        return query


class FooQuery(object):
    """Example of an uncached query."""

    def execute(self, **kwargs):
        self.foos = [1, 2, 3]


@cache_results(timeout=30)
class BarQuery(object):
    """Example of a cached query."""

    def execute(self, option, **kwargs):
        self.bars = ['bar1', 'bar2']


def foos():
    return QueryCache().execute(FooQuery).foos


def bars(option):
    return QueryCache().execute(BarQuery, option).bars
