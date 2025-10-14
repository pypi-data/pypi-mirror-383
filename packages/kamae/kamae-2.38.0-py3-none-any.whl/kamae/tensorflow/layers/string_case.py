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
class StringCaseLayer(BaseLayer):
    """
    Performs a string case transform on the input tensor.
    Supported string case types are 'upper' and 'lower'.
    """

    def __init__(
        self,
        string_case_type: str = "lower",
        name: Optional[str] = None,
        input_dtype: Optional[str] = None,
        output_dtype: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialises the StringCaseLayer layer.

        :param string_case_type: The type of string case transform to perform.
        Supported types are 'upper' and 'lower'. Defaults to 'lower'.
        :param name: The name of the layer. Defaults to `None`.
        :param input_dtype: The dtype to cast the input to. Defaults to `None`.
        :param output_dtype: The dtype to cast the output to. Defaults to `None`.
        """
        super().__init__(
            name=name, input_dtype=input_dtype, output_dtype=output_dtype, **kwargs
        )
        self.string_case_type = string_case_type

    @property
    def compatible_dtypes(self) -> Optional[List[tf.dtypes.DType]]:
        """
        Returns the compatible dtypes of the layer.

        :returns: The compatible dtypes of the layer.
        """
        return [tf.string]

    @enforce_single_tensor_input
    def _call(self, inputs: Tensor, **kwargs: Any) -> Tensor:
        """
        Performs the string case transform on the input tensor.

        Decorated with `@enforce_single_tensor_input` to ensure that the input is a
        single tensor. Raises an error if multiple tensors are passed in as an iterable.

        :param inputs: Input tensor to perform the string case transform on.
        :returns: The input tensor with the string case transform applied.
        """
        if self.string_case_type == "upper":
            return tf.strings.upper(inputs)
        elif self.string_case_type == "lower":
            return tf.strings.lower(inputs)
        else:
            raise ValueError(
                f"""stringCaseType must be one of 'upper' or 'lower'.
                Got {self.string_case_type}"""
            )

    def get_config(self) -> Dict[str, Any]:
        """
        Gets the configuration of the StringCase layer.
        Used for saving and loading from a model.

        Specifically adds the `string_case_type` value to the configuration.

        :returns: Dictionary of the configuration of the layer.
        """
        config = super().get_config()
        config.update({"string_case_type": self.string_case_type})
        return config
