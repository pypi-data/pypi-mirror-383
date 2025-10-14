from src.lib.backends.numpy import FederatedNumpy
from src.lib.backends.torch import FederatedTorch
from src.lib.config import Backend


def get_backend_from_type(cls):
    if issubclass(cls, FederatedTorch):
        return Backend.PYTORCH
    elif issubclass(cls, FederatedNumpy):
        return Backend.NUMPY
    else:
        raise NotImplemented(f"EasyFed doesn't support {cls} types")
