import functools
import inspect
import typing
from functools import partial
from inspect import isclass, ismethod


def get_callable_name(func):
    """
    Returns the best available display name for the given function/callable.
    :rtype: str
    """
    # the easy case (on Python 3.3+)
    if hasattr(func, '__qualname__'):
        return func.__qualname__

    # class methods, bound and unbound methods
    f_self = getattr(func, '__self__', None) or getattr(func, 'im_self', None)
    if f_self and hasattr(func, '__name__'):
        f_class = f_self if isclass(f_self) else f_self.__class__
    else:
        f_class = getattr(func, 'im_class', None)

    if f_class and hasattr(func, '__name__'):
        return '%s.%s' % (f_class.__name__, func.__name__)

    # class or class instance
    if hasattr(func, '__call__'):
        # class
        if hasattr(func, '__name__'):
            return func.__name__

        # instance of a class with a __call__ method
        return func.__class__.__name__

    raise TypeError('Unable to determine a name for %r -- maybe it is not a callable?' % func)


def obj_to_ref(obj):
    """
    将函数或方法等callable对象，序列化成可直接引用的有效包与路径引用串
    Returns the path to the given callable.

    :rtype: str
    :raises TypeError: if the given object is not callable
    :raises ValueError: if the given object is a :class:`~functools.partial`, lambda or a nested
        function

    """
    if isinstance(obj, partial):
        raise ValueError('Cannot create a reference to a partial()')

    name = get_callable_name(obj)
    if '<lambda>' in name:
        raise ValueError('Cannot create a reference to a lambda')
    if '<locals>' in name:
        raise ValueError('Cannot create a reference to a nested function')

    if ismethod(obj):
        if hasattr(obj, 'im_self') and obj.im_self:
            # bound method
            module = obj.im_self.__module__
        elif hasattr(obj, 'im_class') and obj.im_class:
            # unbound method
            module = obj.im_class.__module__
        else:
            module = obj.__module__
    else:
        module = obj.__module__
    return '%s:%s' % (module, name)


def ref_to_obj(ref):
    """
    将包与路径引用串反序列化成可执行对象
    Returns the object pointed to by ``ref``.
    :type ref: str
    """
    if not isinstance(ref, str):
        raise TypeError('References must be strings')
    if ':' not in ref:
        raise ValueError('Invalid reference')

    module_name, rest = ref.split(':', 1)
    try:
        obj = __import__(module_name, fromlist=[rest])
    except ImportError:
        raise LookupError('Error resolving reference %s: could not import module' % ref)

    try:
        for name in rest.split('.'):
            obj = getattr(obj, name)
        return obj
    except Exception:
        raise LookupError('Error resolving reference %s: error looking up object' % ref)


def is_async_callable(obj: typing.Any) -> typing.Any:
    while isinstance(obj, functools.partial):
        obj = obj.func

    return inspect.iscoroutinefunction(obj) or (callable(obj) and inspect.iscoroutinefunction(obj.__call__))
