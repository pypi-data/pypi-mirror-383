# MIT License
# Copyright (c) 2025 aeeeeeep

from types import FrameType
from typing import Any, List, Optional, Tuple

from ..constants import Constants
from ..event_handls import EventHandls
from .abc_wrapper import ABCWrapper

try:
    import torch
except ImportError:
    torch = None  # type: ignore


def process_tensor_item(seq: List[Any]) -> Optional[List[Any]]:
    """
    Process a sequence to extract tensor shapes if all items are torch.Tensor.

    Args:
        seq (List[Any]): The sequence to process.

    Returns:
        Optional[List[Any]]: List of tensor shapes or None if not applicable.
    """
    if torch is not None and all(isinstance(x, torch.Tensor) for x in seq):
        return [x.shape for x in seq]
    else:
        return None


class TensorShapeWrapper(ABCWrapper):
    """
    TensorShapeWrapper extends ABCWrapper to log the shapes of torch.Tensor objects.
    """

    def __init__(self):
        self.format_sequence_func = process_tensor_item

    def wrap_call(self, func_name: str, frame: FrameType) -> str:
        """
        Format the function call information, including tensor shapes if applicable.

        Args:
            func_name (str): Name of the function being called.
            frame (FrameType): The current stack frame.

        Returns:
            str: Formatted call message.
        """
        args, kwargs = self._extract_args_kwargs(frame)
        call_msg = self._format_args_kwargs(args, kwargs)
        return call_msg

    def wrap_return(self, func_name: str, result: Any) -> str:
        """
        Format the function return information, including tensor shapes if applicable.

        Args:
            func_name (str): Name of the function returning.
            result (Any): The result returned by the function.

        Returns:
            str: Formatted return message.
        """
        return_msg = self._format_return(result)
        return return_msg

    def wrap_upd(self, old_value: Any, current_value: Any) -> Tuple[str, str]:
        """
        Format the update information of a variable, including tensor shapes if applicable.

        Args:
            old_value (Any): The old value of the variable.
            current_value (Any): The new value of the variable.

        Returns:
            Tuple[str, str]: Formatted old and new values.
        """
        old_msg = self._format_value(old_value)
        current_msg = self._format_value(current_value)
        return old_msg, current_msg

    def _format_value(self, value: Any, is_return: bool = False) -> str:
        """
        Format a value into a string, logging tensor shapes if applicable.

        Args:
            value (Any): The value to format.
            is_return (bool): Flag indicating if the value is a return value.

        Returns:
            str: Formatted value string.
        """
        if torch is not None and isinstance(value, torch.Tensor):
            formatted = f"{value.shape}"
        elif isinstance(value, Constants.LOG_ELEMENT_TYPES):
            formatted = f"{value}"
        elif isinstance(value, Constants.LOG_SEQUENCE_TYPES):
            formatted_sequence = EventHandls.format_sequence(value, func=self.format_sequence_func)
            if formatted_sequence:
                formatted = f"{formatted_sequence}"
            else:
                formatted = f"(type){type(value).__name__}"
        else:
            try:
                formatted = f"(type){value.__name__}"
            except:
                formatted = f"(type){type(value).__name__}"

        if is_return:
            if isinstance(value, torch.Tensor):
                return f"{value.shape}"
            elif isinstance(value, Constants.LOG_SEQUENCE_TYPES) and formatted:
                return f"[{formatted}]"
            return f"{formatted}"
        return formatted
