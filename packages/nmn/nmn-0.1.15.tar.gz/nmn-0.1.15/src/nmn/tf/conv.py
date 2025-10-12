"""YAT convolution layers for TensorFlow."""

import tensorflow as tf
import math
from typing import Optional, Any, Tuple, Union, List, Callable


class YatConv1D(tf.Module):
    """1D YAT convolution module using TensorFlow operations.
    
    This module implements 1D convolution using the YAT (You Are There) algorithm,
    which computes (dot_product)^2 / (squared_euclidean_distance + epsilon).
    
    Args:
        filters: Integer, the dimensionality of the output space.
        kernel_size: Integer, specifying the length of the 1D convolution window.
        strides: Integer, specifying the stride length of the convolution. Defaults to 1.
        padding: String, either "valid" or "same" (case-insensitive). Defaults to "valid".
        dilation_rate: Integer, dilation rate to use for dilated convolution. Defaults to 1.
        groups: Integer, number of groups for grouped convolution. Defaults to 1.
        use_bias: Boolean, whether to add a bias to the output. Defaults to True.
        use_alpha: Boolean, whether to use alpha scaling. Defaults to True.
        epsilon: Float, small constant for numerical stability. Defaults to 1e-6.
        dtype: The dtype of the computation. Defaults to tf.float32.
        name: Name of the module.
    """
    
    def __init__(
        self,
        filters: int,
        kernel_size: int,
        strides: int = 1,
        padding: str = "valid",
        dilation_rate: int = 1,
        groups: int = 1,
        use_bias: bool = True,
        use_alpha: bool = True,
        epsilon: float = 1e-6,
        dtype: tf.DType = tf.float32,
        name: Optional[str] = None
    ):
        super().__init__(name=name)
        self.filters = filters
        self.kernel_size = kernel_size
        self.strides = strides
        self.padding = padding.upper()
        self.dilation_rate = dilation_rate
        self.groups = groups
        self.use_bias = use_bias
        self.use_alpha = use_alpha
        self.epsilon = epsilon
        self.dtype = dtype
        
        # Variables will be created in build
        self.is_built = False
        self.input_channels = None
        self.kernel = None
        self.bias = None
        self.alpha = None

    @tf.Module.with_name_scope
    def build(self, input_shape: Union[List[int], tf.TensorShape]) -> None:
        """Builds the layer weights based on input shape.
        
        Args:
            input_shape: Shape of the input tensor [batch, length, channels].
        """
        if self.is_built:
            return

        input_channels = int(input_shape[-1])
        self.input_channels = input_channels
        
        if input_channels % self.groups != 0:
            raise ValueError(
                f"Input channels ({input_channels}) must be divisible by groups ({self.groups})"
            )
        
        if self.filters % self.groups != 0:
            raise ValueError(
                f"Filters ({self.filters}) must be divisible by groups ({self.groups})"
            )

        # Kernel shape: [kernel_size, input_channels_per_group, filters]
        channels_per_group = input_channels // self.groups
        kernel_shape = (self.kernel_size, channels_per_group, self.filters)
        
        # Initialize kernel using orthogonal initialization
        kernel_init = tf.random.normal(kernel_shape, dtype=self.dtype)
        # Simple orthogonal-like initialization by normalizing
        kernel_init = kernel_init / tf.sqrt(tf.cast(channels_per_group * self.kernel_size, self.dtype))
        
        self.kernel = tf.Variable(
            kernel_init,
            trainable=True,
            name='kernel',
            dtype=self.dtype
        )

        # Initialize bias
        if self.use_bias:
            self.bias = tf.Variable(
                tf.zeros([self.filters], dtype=self.dtype),
                trainable=True,
                name='bias'
            )

        # Initialize alpha
        if self.use_alpha:
            self.alpha = tf.Variable(
                tf.ones([1], dtype=self.dtype),
                trainable=True,
                name='alpha'
            )

        self.is_built = True

    def _maybe_build(self, inputs: tf.Tensor) -> None:
        """Builds the layer if it hasn't been built yet."""
        if not self.is_built:
            self.build(inputs.shape)

    @tf.Module.with_name_scope
    def __call__(self, inputs: tf.Tensor) -> tf.Tensor:
        """Forward pass of the 1D YAT convolution.
        
        Args:
            inputs: Input tensor of shape [batch, length, channels].
            
        Returns:
            Output tensor after YAT convolution.
        """
        inputs = tf.convert_to_tensor(inputs, dtype=self.dtype)
        self._maybe_build(inputs)

        # Compute dot product using standard convolution
        dot_prod_map = tf.nn.conv1d(
            inputs,
            self.kernel,
            stride=self.strides,
            padding=self.padding,
            dilations=self.dilation_rate,
        )

        # Compute ||input_patches||^2 using convolution with ones kernel
        inputs_squared = inputs * inputs
        
        # Create ones kernel for computing patch squared sums
        ones_kernel_shape = (self.kernel_size, self.input_channels // self.groups, 1)
        ones_kernel = tf.ones(ones_kernel_shape, dtype=self.dtype)
        
        patch_sq_sum_map_raw = tf.nn.conv1d(
            inputs_squared,
            ones_kernel,
            stride=self.strides,
            padding=self.padding,
            dilations=self.dilation_rate,
        )

        # Handle grouped convolution
        if self.groups > 1:
            patch_sq_sum_map = tf.repeat(patch_sq_sum_map_raw, self.filters // self.groups, axis=-1)
        else:
            patch_sq_sum_map = tf.repeat(patch_sq_sum_map_raw, self.filters, axis=-1)

        # Compute ||kernel||^2 per filter
        kernel_sq_sum_per_filter = tf.reduce_sum(self.kernel**2, axis=[0, 1])  # Sum over spatial and input channel dims

        # Reshape for broadcasting: [1, 1, filters]
        kernel_sq_sum_reshaped = tf.reshape(kernel_sq_sum_per_filter, [1, 1, -1])

        # Compute YAT: distance_squared = ||patch||^2 + ||kernel||^2 - 2 * dot_product
        distance_sq_map = patch_sq_sum_map + kernel_sq_sum_reshaped - 2 * dot_prod_map

        # YAT computation: (dot_product)^2 / (distance_squared + epsilon)
        y = dot_prod_map**2 / (distance_sq_map + self.epsilon)

        # Add bias if present
        if self.use_bias:
            y = y + self.bias

        # Apply alpha scaling
        if self.use_alpha and self.alpha is not None:
            scale = tf.pow(
                tf.cast(
                    tf.sqrt(float(self.filters)) / tf.math.log(1. + float(self.filters)),
                    self.dtype
                ),
                self.alpha
            )
            y = y * scale

        return y


class YatConv2D(tf.Module):
    """2D YAT convolution module using TensorFlow operations.
    
    This module implements 2D convolution using the YAT (You Are There) algorithm,
    which computes (dot_product)^2 / (squared_euclidean_distance + epsilon).
    
    Args:
        filters: Integer, the dimensionality of the output space.
        kernel_size: Integer or tuple/list of 2 integers, specifying the height and width
            of the 2D convolution window.
        strides: Integer or tuple/list of 2 integers, specifying the strides of the convolution.
            Defaults to (1, 1).
        padding: String, either "valid" or "same" (case-insensitive). Defaults to "valid".
        dilation_rate: Integer or tuple/list of 2 integers, dilation rate for dilated convolution.
            Defaults to (1, 1).
        groups: Integer, number of groups for grouped convolution. Defaults to 1.
        use_bias: Boolean, whether to add a bias to the output. Defaults to True.
        use_alpha: Boolean, whether to use alpha scaling. Defaults to True.
        epsilon: Float, small constant for numerical stability. Defaults to 1e-6.
        dtype: The dtype of the computation. Defaults to tf.float32.
        name: Name of the module.
    """
    
    def __init__(
        self,
        filters: int,
        kernel_size: Union[int, Tuple[int, int]],
        strides: Union[int, Tuple[int, int]] = (1, 1),
        padding: str = "valid",
        dilation_rate: Union[int, Tuple[int, int]] = (1, 1),
        groups: int = 1,
        use_bias: bool = True,
        use_alpha: bool = True,
        epsilon: float = 1e-6,
        dtype: tf.DType = tf.float32,
        name: Optional[str] = None
    ):
        super().__init__(name=name)
        self.filters = filters
        self.kernel_size = kernel_size if isinstance(kernel_size, (list, tuple)) else (kernel_size, kernel_size)
        self.strides = strides if isinstance(strides, (list, tuple)) else (strides, strides)
        self.padding = padding.upper()
        self.dilation_rate = dilation_rate if isinstance(dilation_rate, (list, tuple)) else (dilation_rate, dilation_rate)
        self.groups = groups
        self.use_bias = use_bias
        self.use_alpha = use_alpha
        self.epsilon = epsilon
        self.dtype = dtype
        
        # Variables will be created in build
        self.is_built = False
        self.input_channels = None
        self.kernel = None
        self.bias = None
        self.alpha = None

    @tf.Module.with_name_scope
    def build(self, input_shape: Union[List[int], tf.TensorShape]) -> None:
        """Builds the layer weights based on input shape.
        
        Args:
            input_shape: Shape of the input tensor [batch, height, width, channels].
        """
        if self.is_built:
            return

        input_channels = int(input_shape[-1])
        self.input_channels = input_channels
        
        if input_channels % self.groups != 0:
            raise ValueError(
                f"Input channels ({input_channels}) must be divisible by groups ({self.groups})"
            )
        
        if self.filters % self.groups != 0:
            raise ValueError(
                f"Filters ({self.filters}) must be divisible by groups ({self.groups})"
            )

        # Kernel shape: [kernel_height, kernel_width, input_channels_per_group, filters]
        channels_per_group = input_channels // self.groups
        kernel_shape = self.kernel_size + (channels_per_group, self.filters)
        
        # Initialize kernel using orthogonal initialization
        kernel_init = tf.random.normal(kernel_shape, dtype=self.dtype)
        # Simple orthogonal-like initialization by normalizing
        kernel_init = kernel_init / tf.sqrt(tf.cast(channels_per_group * self.kernel_size[0] * self.kernel_size[1], self.dtype))
        
        self.kernel = tf.Variable(
            kernel_init,
            trainable=True,
            name='kernel',
            dtype=self.dtype
        )

        # Initialize bias
        if self.use_bias:
            self.bias = tf.Variable(
                tf.zeros([self.filters], dtype=self.dtype),
                trainable=True,
                name='bias'
            )

        # Initialize alpha
        if self.use_alpha:
            self.alpha = tf.Variable(
                tf.ones([1], dtype=self.dtype),
                trainable=True,
                name='alpha'
            )

        self.is_built = True

    def _maybe_build(self, inputs: tf.Tensor) -> None:
        """Builds the layer if it hasn't been built yet."""
        if not self.is_built:
            self.build(inputs.shape)

    @tf.Module.with_name_scope
    def __call__(self, inputs: tf.Tensor) -> tf.Tensor:
        """Forward pass of the 2D YAT convolution.
        
        Args:
            inputs: Input tensor of shape [batch, height, width, channels].
            
        Returns:
            Output tensor after YAT convolution.
        """
        inputs = tf.convert_to_tensor(inputs, dtype=self.dtype)
        self._maybe_build(inputs)

        # Compute dot product using standard convolution
        dot_prod_map = tf.nn.conv2d(
            inputs,
            self.kernel,
            strides=[1] + list(self.strides) + [1],
            padding=self.padding,
            dilations=[1] + list(self.dilation_rate) + [1],
        )

        # Compute ||input_patches||^2 using convolution with ones kernel
        inputs_squared = inputs * inputs
        
        # Create ones kernel for computing patch squared sums
        ones_kernel_shape = self.kernel_size + (self.input_channels // self.groups, 1)
        ones_kernel = tf.ones(ones_kernel_shape, dtype=self.dtype)
        
        patch_sq_sum_map_raw = tf.nn.conv2d(
            inputs_squared,
            ones_kernel,
            strides=[1] + list(self.strides) + [1],
            padding=self.padding,
            dilations=[1] + list(self.dilation_rate) + [1],
        )

        # Handle grouped convolution
        if self.groups > 1:
            patch_sq_sum_map = tf.repeat(patch_sq_sum_map_raw, self.filters // self.groups, axis=-1)
        else:
            patch_sq_sum_map = tf.repeat(patch_sq_sum_map_raw, self.filters, axis=-1)

        # Compute ||kernel||^2 per filter
        kernel_sq_sum_per_filter = tf.reduce_sum(self.kernel**2, axis=[0, 1, 2])  # Sum over spatial and input channel dims

        # Reshape for broadcasting: [1, 1, 1, filters]
        kernel_sq_sum_reshaped = tf.reshape(kernel_sq_sum_per_filter, [1, 1, 1, -1])

        # Compute YAT: distance_squared = ||patch||^2 + ||kernel||^2 - 2 * dot_product
        distance_sq_map = patch_sq_sum_map + kernel_sq_sum_reshaped - 2 * dot_prod_map

        # YAT computation: (dot_product)^2 / (distance_squared + epsilon)
        y = dot_prod_map**2 / (distance_sq_map + self.epsilon)

        # Add bias if present
        if self.use_bias:
            y = y + self.bias

        # Apply alpha scaling
        if self.use_alpha and self.alpha is not None:
            scale = tf.pow(
                tf.cast(
                    tf.sqrt(float(self.filters)) / tf.math.log(1. + float(self.filters)),
                    self.dtype
                ),
                self.alpha
            )
            y = y * scale

        return y


class YatConv3D(tf.Module):
    """3D YAT convolution module using TensorFlow operations.
    
    This module implements 3D convolution using the YAT (You Are There) algorithm,
    which computes (dot_product)^2 / (squared_euclidean_distance + epsilon).
    
    Args:
        filters: Integer, the dimensionality of the output space.
        kernel_size: Integer or tuple/list of 3 integers, specifying the depth, height and width
            of the 3D convolution window.
        strides: Integer or tuple/list of 3 integers, specifying the strides of the convolution.
            Defaults to (1, 1, 1).
        padding: String, either "valid" or "same" (case-insensitive). Defaults to "valid".
        dilation_rate: Integer or tuple/list of 3 integers, dilation rate for dilated convolution.
            Defaults to (1, 1, 1).
        groups: Integer, number of groups for grouped convolution. Defaults to 1.
        use_bias: Boolean, whether to add a bias to the output. Defaults to True.
        use_alpha: Boolean, whether to use alpha scaling. Defaults to True.
        epsilon: Float, small constant for numerical stability. Defaults to 1e-6.
        dtype: The dtype of the computation. Defaults to tf.float32.
        name: Name of the module.
    """
    
    def __init__(
        self,
        filters: int,
        kernel_size: Union[int, Tuple[int, int, int]],
        strides: Union[int, Tuple[int, int, int]] = (1, 1, 1),
        padding: str = "valid",
        dilation_rate: Union[int, Tuple[int, int, int]] = (1, 1, 1),
        groups: int = 1,
        use_bias: bool = True,
        use_alpha: bool = True,
        epsilon: float = 1e-6,
        dtype: tf.DType = tf.float32,
        name: Optional[str] = None
    ):
        super().__init__(name=name)
        self.filters = filters
        self.kernel_size = kernel_size if isinstance(kernel_size, (list, tuple)) else (kernel_size, kernel_size, kernel_size)
        self.strides = strides if isinstance(strides, (list, tuple)) else (strides, strides, strides)
        self.padding = padding.upper()
        self.dilation_rate = dilation_rate if isinstance(dilation_rate, (list, tuple)) else (dilation_rate, dilation_rate, dilation_rate)
        self.groups = groups
        self.use_bias = use_bias
        self.use_alpha = use_alpha
        self.epsilon = epsilon
        self.dtype = dtype
        
        # Variables will be created in build
        self.is_built = False
        self.input_channels = None
        self.kernel = None
        self.bias = None
        self.alpha = None

    @tf.Module.with_name_scope
    def build(self, input_shape: Union[List[int], tf.TensorShape]) -> None:
        """Builds the layer weights based on input shape.
        
        Args:
            input_shape: Shape of the input tensor [batch, depth, height, width, channels].
        """
        if self.is_built:
            return

        input_channels = int(input_shape[-1])
        self.input_channels = input_channels
        
        if input_channels % self.groups != 0:
            raise ValueError(
                f"Input channels ({input_channels}) must be divisible by groups ({self.groups})"
            )
        
        if self.filters % self.groups != 0:
            raise ValueError(
                f"Filters ({self.filters}) must be divisible by groups ({self.groups})"
            )

        # Kernel shape: [kernel_depth, kernel_height, kernel_width, input_channels_per_group, filters]
        channels_per_group = input_channels // self.groups
        kernel_shape = self.kernel_size + (channels_per_group, self.filters)
        
        # Initialize kernel using orthogonal initialization
        kernel_init = tf.random.normal(kernel_shape, dtype=self.dtype)
        # Simple orthogonal-like initialization by normalizing
        fan_in = channels_per_group * self.kernel_size[0] * self.kernel_size[1] * self.kernel_size[2]
        kernel_init = kernel_init / tf.sqrt(tf.cast(fan_in, self.dtype))
        
        self.kernel = tf.Variable(
            kernel_init,
            trainable=True,
            name='kernel',
            dtype=self.dtype
        )

        # Initialize bias
        if self.use_bias:
            self.bias = tf.Variable(
                tf.zeros([self.filters], dtype=self.dtype),
                trainable=True,
                name='bias'
            )

        # Initialize alpha
        if self.use_alpha:
            self.alpha = tf.Variable(
                tf.ones([1], dtype=self.dtype),
                trainable=True,
                name='alpha'
            )

        self.is_built = True

    def _maybe_build(self, inputs: tf.Tensor) -> None:
        """Builds the layer if it hasn't been built yet."""
        if not self.is_built:
            self.build(inputs.shape)

    @tf.Module.with_name_scope
    def __call__(self, inputs: tf.Tensor) -> tf.Tensor:
        """Forward pass of the 3D YAT convolution.
        
        Args:
            inputs: Input tensor of shape [batch, depth, height, width, channels].
            
        Returns:
            Output tensor after YAT convolution.
        """
        inputs = tf.convert_to_tensor(inputs, dtype=self.dtype)
        self._maybe_build(inputs)

        # Compute dot product using standard convolution
        dot_prod_map = tf.nn.conv3d(
            inputs,
            self.kernel,
            strides=[1] + list(self.strides) + [1],
            padding=self.padding,
            dilations=[1] + list(self.dilation_rate) + [1],
        )

        # Compute ||input_patches||^2 using convolution with ones kernel
        inputs_squared = inputs * inputs
        
        # Create ones kernel for computing patch squared sums
        ones_kernel_shape = self.kernel_size + (self.input_channels // self.groups, 1)
        ones_kernel = tf.ones(ones_kernel_shape, dtype=self.dtype)
        
        patch_sq_sum_map_raw = tf.nn.conv3d(
            inputs_squared,
            ones_kernel,
            strides=[1] + list(self.strides) + [1],
            padding=self.padding,
            dilations=[1] + list(self.dilation_rate) + [1],
        )

        # Handle grouped convolution
        if self.groups > 1:
            patch_sq_sum_map = tf.repeat(patch_sq_sum_map_raw, self.filters // self.groups, axis=-1)
        else:
            patch_sq_sum_map = tf.repeat(patch_sq_sum_map_raw, self.filters, axis=-1)

        # Compute ||kernel||^2 per filter
        kernel_sq_sum_per_filter = tf.reduce_sum(self.kernel**2, axis=[0, 1, 2, 3])  # Sum over spatial and input channel dims

        # Reshape for broadcasting: [1, 1, 1, 1, filters]
        kernel_sq_sum_reshaped = tf.reshape(kernel_sq_sum_per_filter, [1, 1, 1, 1, -1])

        # Compute YAT: distance_squared = ||patch||^2 + ||kernel||^2 - 2 * dot_product
        distance_sq_map = patch_sq_sum_map + kernel_sq_sum_reshaped - 2 * dot_prod_map

        # YAT computation: (dot_product)^2 / (distance_squared + epsilon)
        y = dot_prod_map**2 / (distance_sq_map + self.epsilon)

        # Add bias if present
        if self.use_bias:
            y = y + self.bias

        # Apply alpha scaling
        if self.use_alpha and self.alpha is not None:
            scale = tf.pow(
                tf.cast(
                    tf.sqrt(float(self.filters)) / tf.math.log(1. + float(self.filters)),
                    self.dtype
                ),
                self.alpha
            )
            y = y * scale

        return y


# Aliases for backward compatibility
YatConv1d = YatConv1D
YatConv2d = YatConv2D
YatConv3d = YatConv3D