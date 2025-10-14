from typing import Callable, get_args, ForwardRef
from inspect import signature, getsourcefile
from runpy import run_path

from .widgets.control.base import Control
from .widgets.chart.type import Chart

from pydantic import BaseModel


class Callback(BaseModel):
    endpoint_name: str
    trigger_event: str
    inputs: list[str]
    targets: list[str]
    target_wrapper_ids: str


def construct_callback(
    callback_fn: Callable,
    endpoint_name: str,
    trigger_event: str,
) -> Callback:
    sig = signature(callback_fn)
    input_ids: list[str] = []
    target_ids: list[str] = []

    for param in sig.parameters:
        if param == "self" or param == "selected":
            continue
        annotation = sig.parameters[param].annotation
        args = get_args(annotation)

        try:
            widget_type = args[0]
            widget_id = args[1]
        except IndexError:
            continue

        if isinstance(widget_type, ForwardRef):
            source_file = getsourcefile(callback_fn)
            assert source_file is not None
            file_globals = run_path(source_file)
            widget_type = file_globals[widget_type.__forward_arg__]

        if issubclass(widget_type, Control):
            input_ids.append(widget_id + "-input")

        if issubclass(widget_type, Chart):
            target_ids.append(widget_id)

    return Callback(
        endpoint_name=endpoint_name,
        trigger_event=trigger_event,
        inputs=input_ids,
        targets=target_ids,
        target_wrapper_ids=", ".join([f"#{target}-wrapper" for target in target_ids]),
    )
