"""TensorFlow backend for Neural Matter Network (NMN)."""

from .nmn import YatNMN, YatDense

try:
    from .conv import YatConv1D, YatConv2D, YatConv3D, YatConv1d, YatConv2d, YatConv3d
    __all__ = ["YatNMN", "YatDense", "YatConv1D", "YatConv2D", "YatConv3D", "YatConv1d", "YatConv2d", "YatConv3d"]
except ImportError:
    # In case conv module fails to import
    __all__ = ["YatNMN", "YatDense"]