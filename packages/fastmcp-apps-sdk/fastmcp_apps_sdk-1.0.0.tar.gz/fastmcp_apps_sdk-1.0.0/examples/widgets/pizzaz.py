from __future__ import annotations

from fastmcp_apps_sdk import WidgetToolResponse, build_widget_tool_response, widget

PizzaTopping = str


def _normalize_topping(pizza_topping: str) -> str:
    normalized = pizza_topping.strip()
    if not normalized:
        raise ValueError("Provide a pizza topping to render the widget.")
    return normalized


@widget(
    identifier="pizza-map",
    title="Show Pizza Map",
    template_uri="ui://widget/pizza-map.html",
    invoking="Hand-tossing a map",
    invoked="Served a fresh map",
    html=(
        '<div id="pizzaz-root"></div>\n'
        '<link rel="stylesheet" href="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-0038.css">\n'
        '<script type="module" src="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-0038.js"></script>'
    ),
    description="Show Pizza Map",
)
def show_pizza_map_widget(pizza_topping: PizzaTopping) -> WidgetToolResponse:
    normalized = _normalize_topping(pizza_topping)
    return build_widget_tool_response(
        response_text="Rendered a pizza map!",
        structured_content={"pizza_topping": normalized},
    )


@widget(
    identifier="pizza-carousel",
    title="Show Pizza Carousel",
    template_uri="ui://widget/pizza-carousel.html",
    invoking="Carousel some spots",
    invoked="Served a fresh carousel",
    html=(
        '<div id="pizzaz-carousel-root"></div>\n'
        '<link rel="stylesheet" href="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-carousel-0038.css">\n'
        '<script type="module" src="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-carousel-0038.js"></script>'
    ),
    description="Show Pizza Carousel",
)
def show_pizza_carousel_widget(pizza_topping: PizzaTopping) -> WidgetToolResponse:
    normalized = _normalize_topping(pizza_topping)
    return build_widget_tool_response(
        response_text="Rendered a pizza carousel!",
        structured_content={"pizza_topping": normalized},
    )


@widget(
    identifier="pizza-albums",
    title="Show Pizza Album",
    template_uri="ui://widget/pizza-albums.html",
    invoking="Hand-tossing an album",
    invoked="Served a fresh album",
    html=(
        '<div id="pizzaz-albums-root"></div>\n'
        '<link rel="stylesheet" href="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-albums-0038.css">\n'
        '<script type="module" src="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-albums-0038.js"></script>'
    ),
    description="Show Pizza Album",
)
def show_pizza_album_widget(pizza_topping: PizzaTopping) -> WidgetToolResponse:
    normalized = _normalize_topping(pizza_topping)
    return build_widget_tool_response(
        response_text="Rendered a pizza album!",
        structured_content={"pizza_topping": normalized},
    )


@widget(
    identifier="pizza-list",
    title="Show Pizza List",
    template_uri="ui://widget/pizza-list.html",
    invoking="Hand-tossing a list",
    invoked="Served a fresh list",
    html=(
        '<div id="pizzaz-list-root"></div>\n'
        '<link rel="stylesheet" href="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-list-0038.css">\n'
        '<script type="module" src="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-list-0038.js"></script>'
    ),
    description="Show Pizza List",
)
def show_pizza_list_widget(pizza_topping: PizzaTopping) -> WidgetToolResponse:
    normalized = _normalize_topping(pizza_topping)
    return build_widget_tool_response(
        response_text="Rendered a pizza list!",
        structured_content={"pizza_topping": normalized},
    )


@widget(
    identifier="pizza-video",
    title="Show Pizza Video",
    template_uri="ui://widget/pizza-video.html",
    invoking="Hand-tossing a video",
    invoked="Served a fresh video",
    html=(
        '<div id="pizzaz-video-root"></div>\n'
        '<link rel="stylesheet" href="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-video-0038.css">\n'
        '<script type="module" src="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-video-0038.js"></script>'
    ),
    description="Show Pizza Video",
)
def show_pizza_video_widget(pizza_topping: PizzaTopping) -> WidgetToolResponse:
    normalized = _normalize_topping(pizza_topping)
    return build_widget_tool_response(
        response_text="Rendered a pizza video!",
        structured_content={"pizza_topping": normalized},
    )
