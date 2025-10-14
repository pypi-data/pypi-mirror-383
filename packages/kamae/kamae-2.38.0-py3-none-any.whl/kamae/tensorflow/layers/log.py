# Copyright [2024] Expedia, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, Dict, List, Optional

import tensorflow as tf

import kamae
from kamae.tensorflow.typing import Tensor
from kamae.tensorflow.utils import enforce_single_tensor_input

from .base import BaseLayer


@tf.keras.utils.register_keras_serializable(package=kamae.__name__)
class LogLayer(BaseLayer):
    """
    Performs the log(alpha + x) operation on a given input tensor
    """

    def __init__(
        self,
        name: Optional[str] = None,
        input_dtype: Optional[str] = None,
        output_dtype: Optional[str] = None,
        alpha: float = 0.0,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the LogLayer layer

        :param name: Name of the layer, defaults to `None`.
        :param input_dtype: The dtype to cast the input to. Defaults to `None`.
        :param output_dtype: The dtype to cast the output to. Defaults to `None`.
        :param alpha: Alpha value to use in the log(alpha + x) operation,
        defaults to 0.0.
        """
        super().__init__(
            name=name, input_dtype=input_dtype, output_dtype=output_dtype, **kwargs
        )
        self.alpha = alpha

    @property
    def compatible_dtypes(self) -> Optional[List[tf.dtypes.DType]]:
        """
        Returns the compatible dtypes of the layer.

        :returns: The compatible dtypes of the layer.
        """
        return [
            tf.bfloat16,
            tf.float16,
            tf.float32,
            tf.float64,
            tf.complex64,
            tf.complex128,
        ]

    @enforce_single_tensor_input
    def _call(self, inputs: Tensor, **kwargs: Any) -> Tensor:
        """
        Performs the log(alpha + x) operation on a given input tensor

        Decorated with `@enforce_single_tensor_input` to ensure that
        the input is a single tensor. Raises an error if multiple tensors are passed
        in as an iterable.

        :param inputs: Input tensor to perform the log(alpha + x) operation on.
        :returns: The input tensor with the log(alpha + x) operation applied.
        """
        return tf.math.log(tf.math.add(inputs, self.alpha))

    def get_config(self) -> Dict[str, Any]:
        """
        Gets the configuration of the LogAlphaP layer.
        Used for saving and loading from a model.

        Specifically adds the `alpha` value to the configuration.

        :returns: Dictionary of the configuration of the layer.
        """
        config = super().get_config()
        config.update({"alpha": self.alpha})
        return config
