from __future__ import annotations

from fastmcp_apps_sdk import WidgetToolResponse, build_widget_tool_response, widget


PLANETS = [
    "Mercury",
    "Venus",
    "Earth",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
]

PLANET_ALIASES = {
    "terra": "Earth",
    "gaia": "Earth",
    "soliii": "Earth",
    "tellus": "Earth",
    "ares": "Mars",
    "jove": "Jupiter",
    "zeus": "Jupiter",
    "cronus": "Saturn",
    "ouranos": "Uranus",
    "poseidon": "Neptune",
}

PLANET_DESCRIPTIONS = {
    "Mercury": "Mercury is the smallest planet in the Solar System and the closest to the Sun. It has a rocky, cratered surface and extreme temperature swings.",
    "Venus": "Venus, similar in size to Earth, is cloaked in thick clouds of sulfuric acid with surface temperatures hot enough to melt lead.",
    "Earth": "Earth is the only known planet to support life, with liquid water covering most of its surface and a protective atmosphere.",
    "Mars": "Mars, the Red Planet, shows evidence of ancient rivers and volcanoes and is a prime target in the search for past life.",
    "Jupiter": "Jupiter is the largest planet, a gas giant with a Great Red Spot—an enormous storm raging for centuries.",
    "Saturn": "Saturn is famous for its stunning ring system composed of billions of ice and rock particles orbiting the planet.",
    "Uranus": "Uranus is an ice giant rotating on its side, giving rise to extreme seasonal variations during its long orbit.",
    "Neptune": "Neptune, the farthest known giant, is a deep-blue world with supersonic winds and a faint ring system.",
}

DEFAULT_PLANET = "Earth"


def _normalize_planet(name: str | None) -> str | None:
    if not name:
        return DEFAULT_PLANET

    key = name.strip().lower()
    if not key:
        return DEFAULT_PLANET

    clean = "".join(ch for ch in key if ch.isalnum())

    for planet in PLANETS:
        planet_key = "".join(ch for ch in planet.lower() if ch.isalnum())
        if clean == planet_key or key == planet.lower():
            return planet

    alias = PLANET_ALIASES.get(clean)
    if alias:
        return alias

    for planet in PLANETS:
        planet_key = "".join(ch for ch in planet.lower() if ch.isalnum())
        if planet_key.startswith(clean):
            return planet

    return None


@widget(
    identifier="solar-system",
    title="Explore the Solar System",
    template_uri="ui://widget/solar-system.html",
    invoking="Charting the solar system",
    invoked="Solar system ready",
    html=(
        '<div id="solar-system-root"></div>\n'
        '<link rel="stylesheet" href="https://persistent.oaistatic.com/ecosystem-built-assets/solar-system-0038.css">\n'
        '<script type="module" src="https://persistent.oaistatic.com/ecosystem-built-assets/solar-system-0038.js"></script>'
    ),
    description="Render the solar system widget centered on the requested planet.",
)
def solar_system(
    planet_name: str = DEFAULT_PLANET,
    auto_orbit: bool = True,
) -> WidgetToolResponse:
    planet = _normalize_planet(planet_name)
    if planet is None:
        raise ValueError("Unknown planet. Provide one of: " + ", ".join(PLANETS))

    return build_widget_tool_response(
        response_text="Solar system ready",
        structured_content={
            "planet": planet,
            "description": PLANET_DESCRIPTIONS.get(planet, ""),
            "auto_orbit": bool(auto_orbit),
        },
    )

