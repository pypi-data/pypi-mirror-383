"""
Some decorators that simplify Python code
"""
try:
    from time import perf_counter
except:
    from time import clock as perf_counter
from logging import disable,INFO
import sys
from os import devnull
from functools import wraps
def timer(x):
    """
    Calculates the time running function x. Uses time.perf_counter() if available, otherwise uses time.clock().
    :param x: The function which needs to be called
    :return: (t,r), t is the time used by x, r is the return value of x
    """
    @wraps(x)
    def a(*args,**kwargs):
        m=perf_counter()
        n=x(*args,**kwargs)
        return (n,perf_counter()-m)
    return a
def noexcept(x):
    """
    Calls the function x, ignores any exception tracebacks.
    :param x: The function which needs to be called
    :return: If x throws an exception, None, otherwise the return value of x
    """
    @wraps(x)
    def s(*args,**kwargs):
        try:
            m=x(*args,**kwargs)
        except:
            return None
        else:
            return m
    return s
def cexcept(x):
    """
    Calls the function x, catches any exceptions raised.
    :param x: The function which needs to be called
    :return: A tuple (ret,exc). ret is None or the return value of x, exc is None or the exception raised.
    """
    @wraps(x)
    def s(*args,**kwargs):
        try:
            m=x(*args,**kwargs)
        except BaseException as e:
            return (None,e)
        else:
            return (m,None)
    return s
def block(x):
    """
    Calls the function x,ignores all output and logs.
    :param x: The function which needs to be called
    :return: The return value of x
    """
    @wraps(x)
    def s(*args,**kwargs):
        k,q=sys.stdout,sys.stderr
        disable(sys.maxsize)
        sys.stdout=sys.stderr=open(devnull,'w')
        m=x(*args,**kwargs)
        disable(INFO)
        sys.stdout=k
        sys.stderr=q
        return m
    return s
def nolog(x):
    """
    Calls the function x, ignores all logs.
    :param x: The function which needs to be called
    :return: The return value of x
    """
    @wraps(x)
    def s(*args,**kwargs):
        disable(sys.maxsize)
        m=x(*args,**kwargs)
        disable(INFO)
        return m
    return s
def tnexcept(*args,**kw):
    """
    Repeat calling the function x until it doesn't raise an exception, all the exceptions raised before are ignored
    :param x: The function which needs to be called
    :param handler: Optional, handler for AssertionError
    :return: The return value of x's last call
    """
    if kw:
        handler=kw['handler']
        def inner(x):
            @wraps(x)
            def s(*args,**kwargs):
                res=None
                while 1:
                    try:
                        res = x(*args, **kwargs)
                    except AssertionError as e:
                        handler(str(e))
                    except:
                        pass
                    else:
                        return res
            return s
        return inner
    else:
        x=args[0]
        @wraps(x)
        def s(*args,**kwargs):
            res=None
            while 1:
                try:
                    res = x(*args, **kwargs)
                except:
                    pass
                else:
                    return res
        return s
def repeat(num):
    """
    Repeat calling the function num times.
    :param num: The number of times
    :return: A list containing all return values of the function's calls
    """
    @wraps(x)
    def f(x):
        def s(*args,**kwargs):
            l=[]
            for i in range(num):
                l.append(x(*args,**kwargs))
            return l
        return s
    return f
def foreach(iterable):
    """
    Repeat calling the function for each object in an iterable.
    Warning: This decorator will pass the current object in the iterable to the first argument of the function, and pass the first argument passed to the decorator to the second argument of the function,the second to the third, etc.
    :param num:The number of times
    :return: A list containing all return values of the function's calls
    """
    @wraps(x)
    def f(x):
        def s(*args,**kwargs):
            l=[]
            for i in iterable:
                l.append(x(*((i,)+args),**kwargs))
            return l
        return s
    return f
TM=timer
NE=noexcept
CE=cexcept
BL=block
NL=nolog
TE=tnexcept
RP=repeat
FE=foreach
__all__=['timer','noexcept','cexcept','block','nolog','tnexcept','repeat','foreach']+['TM', 'NE', 'CE', 'BL', 'NL', 'TE', 'RP', 'FE']
__version__='1.0.0'