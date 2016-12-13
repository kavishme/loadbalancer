from functools import wraps
from datetime import datetime, timedelta

class CircuitBreaker(object):
    def __init__(self, name=None, expected_exception=Exception, max_failure_to_open=3, reset_timeout=10):
        self._name = name
        self._expected_exception = expected_exception
        self._max_failure_to_open = max_failure_to_open
        self._reset_timeout = reset_timeout
        self._is_closed = {}
        self._failure_count = {}
        self._opened_since = {}
        self._open_until = {}
        self._open_remaining = {}
        # Set the initial state
        # self.close()
 
    def close(self, port):
        self._is_closed[port] = True
        self._failure_count[port] = 0
        
    def open(self, port):
        self._is_closed[port] = False
        self._opened_since[port] = datetime.utcnow()
        
    def can_execute(self, port):
        if not self._is_closed[port]:
            self._open_until[port] = self._opened_since[port] + timedelta(seconds=self._reset_timeout)
            self._open_remaining[port] = (self._open_until[port] - datetime.utcnow()).total_seconds()
            return self._open_remaining[port] <= 0
        else:
            return True

    def __call__(self, func):
        if self._name is None:
            self._name = func.__name__

        @wraps(func)
        def with_circuitbreaker(*args, **kwargs):
            return self.call(func, *args, **kwargs)

        return with_circuitbreaker

    def call(self, func, *args, **kwargs):
        port = kwargs['port']
        if not self.can_execute(port):
            err = 'Port Failure %d' % (port)
            raise Exception(err)
        try:
            result = func(*args, **kwargs)
        except self._expected_exception:
            self._failure_count[port] += 1
            if self._failure_count[port] >= self._max_failure_to_open:
                self.open(port)
            raise

        self.close(port)
        return result