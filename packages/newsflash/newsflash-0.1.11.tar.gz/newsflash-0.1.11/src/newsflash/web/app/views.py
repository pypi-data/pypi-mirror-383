from inspect import signature, getsourcefile
from typing import get_args, ForwardRef, Callable, Type, Literal
import json
from enum import StrEnum
from runpy import run_path

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from newsflash import App
from newsflash.widgets.base import Widget
from newsflash.widgets.chart.base import Chart
from newsflash.widgets.control.select import Select
from newsflash.widgets.text.base import Text
from newsflash.widgets import Button


type ChartDimension = dict[Literal["width"] | Literal["height"], float]
type ChartDimensions = dict[str, ChartDimension]


def parse_chart_dimensions(request: HttpRequest) -> ChartDimensions:
    dimensions = request.POST["dimensions"]
    assert isinstance(dimensions, str)
    chart_dimensions = [
        {k.removesuffix("-container"): v for k, v in chart.items()}
        for chart in json.loads(dimensions)
    ]

    chart_dimensions_dict: ChartDimensions = {}
    for chart in chart_dimensions:
        chart_dimensions_dict.update(chart)

    return chart_dimensions_dict


def parse_additional_inputs(request: HttpRequest, trigger: str) -> dict[str, str]:
    additional_inputs: dict[str, str] = {}

    for k in request.POST:
        if k.endswith("-value") and k.removesuffix("-value") != trigger:
            _value = request.POST[k]
            assert isinstance(_value, str)
            additional_inputs[k.removesuffix("-value")] = _value

    return additional_inputs


def parse_request_inputs(
    request: HttpRequest,
) -> tuple[str, dict[str, str], ChartDimensions]:
    trigger: str = request.headers["Hx-Trigger"]  # type: ignore
    additional_inputs = parse_additional_inputs(request, trigger)
    chart_dimensions_dict = parse_chart_dimensions(request)
    return trigger, additional_inputs, chart_dimensions_dict


def resolve_forward_ref(
    widget_type: Type[Widget], callback_fn: Callable
) -> Type[Widget]:
    if isinstance(widget_type, ForwardRef):
        source_file = getsourcefile(callback_fn)
        assert source_file is not None
        file_globals = run_path(source_file)
        widget_type = file_globals[widget_type.__forward_arg__]

    return widget_type


class WidgetIO(StrEnum):
    INPUT = "input"
    OUTPUT = "output"
    BOTH = "input+output"


def process_callback_arg(
    callback_fn: Callable, parameter: str
) -> tuple[Type[Widget], str, WidgetIO]:
    sig = signature(callback_fn)
    annotation = sig.parameters[parameter].annotation
    args = get_args(annotation)

    widget_type = args[0]
    widget_type = resolve_forward_ref(widget_type, callback_fn)
    widget_id = args[1]

    try:
        widget_io = args[2]
    except IndexError:
        if issubclass(widget_type, Select) or issubclass(widget_type, Button):
            widget_io = WidgetIO.INPUT
        elif issubclass(widget_type, Chart) or issubclass(widget_type, Text):
            widget_io = WidgetIO.OUTPUT
        else:
            raise ValueError(f"unexpected widget_type: {widget_type}")

    return widget_type, widget_id, widget_io


def render_callback_outputs(
    callback_outputs: dict[str, Widget], request: HttpRequest
) -> bytes:
    result: str = ""

    for callback_output in callback_outputs.values():
        if callback_output._cancel_update:
            continue
        if isinstance(callback_output, Chart):
            result += "\n" + callback_output.render_chart(
                request, authenticated=request.user.is_authenticated
            )
        else:
            result += "\n" + callback_output.render(request)

    return result.encode()


def get_callback_in_and_outputs(
    callback_fn: Callable,
    additional_inputs: dict[str, str],
    chart_dimensions_dict: ChartDimensions,
) -> tuple[dict[str, Widget], dict[str, Widget]]:
    sig = signature(callback_fn)

    callback_inputs: dict[str, Widget] = {}
    callback_outputs: dict[str, Widget] = {}
    for param in sig.parameters:
        if param == "self" or param == "selected":
            continue

        widget_type, widget_id, widget_io = process_callback_arg(callback_fn, param)
        widget_type = resolve_forward_ref(widget_type, callback_fn)

        if issubclass(widget_type, Select):
            widget = widget_type(selected=additional_inputs[widget_id])

        if issubclass(widget_type, Chart):
            widget = widget_type(
                width_in_px=chart_dimensions_dict[widget_id]["width"],
                height_in_px=chart_dimensions_dict[widget_id]["height"],
                swap_oob=True,
            )

        if issubclass(widget_type, Text):
            widget = widget_type()

        callback_inputs[param] = widget
        if widget_io == WidgetIO.OUTPUT or widget_io == WidgetIO.BOTH:
            widget.swap_oob = True
            callback_outputs[param] = widget

    return callback_inputs, callback_outputs


def build_main_view(app: Type[App]) -> Callable:
    def main(request: HttpRequest, page_num: int = 1) -> HttpResponse:
        _app = app()
        return render(
            request,
            "app/page.html",
            context={
                "content": _app.render(request),
                "page_num": page_num,
                "navbar": _app.navbar,
            },
        )

    return main


def build_button_view(app: Type[App]) -> Callable:
    def click(request: HttpRequest) -> HttpResponse:
        trigger, additional_inputs, chart_dimensions_dict = parse_request_inputs(
            request
        )

        _app = app()
        button_element = _app.query_one(trigger, Button)
        assert button_element is not None

        callback_inputs, callback_outputs = get_callback_in_and_outputs(
            button_element.on_click, additional_inputs, chart_dimensions_dict
        )

        button_element.on_click(**callback_inputs)
        return HttpResponse(render_callback_outputs(callback_outputs, request))

    return click


def build_select_view(app: Type[App]) -> Callable:
    def select(request: HttpRequest) -> HttpResponse:
        trigger, additional_inputs, chart_dimensions_dict = parse_request_inputs(
            request
        )
        trigger = trigger.removesuffix("-input")
        value = request.POST[f"{trigger}-value"]

        _app = app()
        select_element = _app.query_one(trigger, Select)
        assert select_element is not None

        callback_inputs, callback_outputs = get_callback_in_and_outputs(
            select_element.on_input, additional_inputs, chart_dimensions_dict
        )

        value_type = type(select_element.selected)
        select_element.selected = value_type(value)
        select_element.on_input(**callback_inputs)

        return HttpResponse(render_callback_outputs(callback_outputs, request))

    return select


def build_chart_view(app: Type[App]) -> Callable:
    def chart(request: HttpRequest) -> HttpResponse:
        trigger, additional_inputs, chart_dimensions_dict = parse_request_inputs(
            request
        )
        trigger = trigger.removesuffix("-wrapper")

        _app = app()
        chart_element = _app.query_one(trigger, Chart)
        assert chart_element is not None

        chart_element.width_in_px = chart_dimensions_dict[trigger]["width"]
        chart_element.height_in_px = chart_dimensions_dict[trigger]["height"]

        callback_inputs, callback_outputs = get_callback_in_and_outputs(
            chart_element.on_load, additional_inputs, chart_dimensions_dict
        )

        callback_outputs[trigger] = chart_element
        chart_element.on_load(**callback_inputs)

        return HttpResponse(render_callback_outputs(callback_outputs, request))

    return chart
