from triplethreading._core import hello_from_bin
from triplethreading.model import LinearRegression

def hello() -> str:
    return hello_from_bin()

__all__ = ['LinearRegression']
