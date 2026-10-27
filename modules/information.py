"""
modules/information.py — DOT Information Module

Handles:
- Weather (OpenWeatherMap, requires API key in settings)
- Dictionary definitions (dictionaryapi.dev — no key needed)
- Calculator / unit converter
- Trivia facts
- Jokes
"""

from __future__ import annotations

import math
import operator
import random
from typing import Any

import config as cfg
from core.command_registry import CommandRegistry, make_command
from core.logger import get_logger

log = get_logger("information")

# ── trivia ─────────────────────────────────────────────────────────────────────
_TRIVIA: list[str] = [
    "Honey never spoils — archaeologists found 3,000-year-old honey in Egyptian tombs.",
    "A day on Venus is longer than a year on Venus.",
    "Octopuses have three hearts and blue blood.",
    "The Eiffel Tower can grow by 15 cm in summer due to thermal expansion.",
    "Bananas are berries, but strawberries are not.",
    "A group of flamingos is called a flamboyance.",
    "Water can boil and freeze at the same time — it's called the triple point.",
    "The shortest war in history lasted 38 to 45 minutes (Anglo-Zanzibar War, 1896).",
    "There are more possible iterations of a game of chess than atoms in the observable universe.",
    "Sharks are older than trees — they have existed for over 400 million years.",
    "The average person walks about 100,000 miles in a lifetime.",
    "A bolt of lightning is five times hotter than the surface of the sun.",
    "Crows can recognize human faces and hold grudges.",
    "The human brain uses about 20% of the body's total energy.",
    "There are more stars in the universe than grains of sand on all Earth's beaches.",
]

# ── jokes ──────────────────────────────────────────────────────────────────────
_JOKES_CLEAN: list[str] = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I asked my computer to play me some music. It said: 'Error 404 — beat not found.'",
    "Why can't you trust an atom? Because they make up everything.",
    "I told a joke about UDP once. I don't know if you got it.",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
    "Why did the developer go broke? Because they used up all their cache.",
    "There are 10 types of people: those who understand binary and those who don't.",
    "Debugging is like being the detective in a crime movie where you are also the murderer.",
    "Why do Python developers wear glasses? Because they can't C.",
    "A programmer's partner says 'Go to the store, get a gallon of milk, and if they have eggs, get a dozen.'"
    " The programmer came home with 12 gallons of milk.",
]

_JOKES_DARK: list[str] = [
    "Why do graveyards have fences? Because people are dying to get in.",
    "I used to hate funerals, but I'm starting to dig them.",
    "My therapist told me I have trouble letting go. We'll see about that.",
    "I asked the librarian if they had books about paranoia. She whispered: 'They're right behind you.'",
]


# ══════════════════════════════════════════════════════════════════════════════
# Weather
# ══════════════════════════════════════════════════════════════════════════════

def get_weather(city: str = "", **_) -> str:
    try:
        import requests
    except ImportError:
        return "✗ 'requests' package not installed."

    settings = cfg.load_settings()
    api_key = settings.get("weather_api_key", "").strip()
    if not api_key:
        return (
            "✗ No weather API key set.\n"
            "  Run: set weather api key <YOUR_KEY>\n"
            "  Get a free key at: openweathermap.org"
        )

    query_city = city.strip() if city else "auto"
    if query_city == "auto":
        try:
            r = requests.get("https://ipapi.co/json/", timeout=5)
            query_city = r.json().get("city", "London")
        except Exception:
            query_city = "London"

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={query_city}&appid={api_key}&units=metric"
    )
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 401:
            return "✗ Invalid API key."
        if resp.status_code == 404:
            return f"✗ City not found: {query_city}"
        resp.raise_for_status()
        data = resp.json()
        name = data.get("name", query_city)
        desc = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        return (
            f"Weather in {name}:\n"
            f"  {desc}\n"
            f"  Temperature : {temp:.1f}°C  (feels like {feels:.1f}°C)\n"
            f"  Humidity    : {humidity}%\n"
            f"  Wind        : {wind} m/s"
        )
    except Exception as exc:
        log.exception("Weather fetch failed")
        return f"✗ Weather error: {exc}"


def set_api_key(key: str, **_) -> str:
    cfg.set_key("weather_api_key", key.strip())
    return "✓ Weather API key saved."


# ══════════════════════════════════════════════════════════════════════════════
# Dictionary
# ══════════════════════════════════════════════════════════════════════════════

def define_word(word: str, **_) -> str:
    try:
        import requests
    except ImportError:
        return "✗ 'requests' package not installed."

    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.strip()}"
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 404:
            return f"✗ No definition found for: {word}"
        resp.raise_for_status()
        data = resp.json()
        meanings = data[0].get("meanings", [])
        if not meanings:
            return f"✗ No meanings found for: {word}"

        lines = [f"Definition of '{word}':"]
        for m in meanings[:2]:
            pos = m.get("partOfSpeech", "")
            defs = m.get("definitions", [])
            if defs:
                defn = defs[0].get("definition", "")
                lines.append(f"  [{pos}] {defn}")
                example = defs[0].get("example", "")
                if example:
                    lines.append(f"    e.g. \"{example}\"")
        return "\n".join(lines)
    except Exception as exc:
        log.exception("Dictionary lookup failed")
        return f"✗ Dictionary error: {exc}"


# ══════════════════════════════════════════════════════════════════════════════
# Calculator
# ══════════════════════════════════════════════════════════════════════════════

def calculate(expression: str, **_) -> str:
    expr = expression.strip()
    # Replace common words
    expr = expr.replace("^", "**").replace("x", "*").replace("×", "*").replace("÷", "/")
    safe_names: dict[str, Any] = {
        name: getattr(math, name) for name in dir(math) if not name.startswith("_")
    }
    safe_names.update({"abs": abs, "round": round})
    try:
        result = eval(expr, {"__builtins__": {}}, safe_names)  # noqa: S307
        return f"= {result}"
    except ZeroDivisionError:
        return "✗ Division by zero."
    except Exception:
        return f"✗ Could not evaluate: {expression}"


# ══════════════════════════════════════════════════════════════════════════════
# Unit Converter
# ══════════════════════════════════════════════════════════════════════════════

_UNIT_TABLE: dict[str, tuple[str, float]] = {
    # length → metres
    "m": ("length", 1.0), "meter": ("length", 1.0), "metres": ("length", 1.0),
    "km": ("length", 1000.0), "kilometre": ("length", 1000.0), "kilometers": ("length", 1000.0),
    "cm": ("length", 0.01), "centimetre": ("length", 0.01),
    "mm": ("length", 0.001), "millimetre": ("length", 0.001),
    "mile": ("length", 1609.344), "miles": ("length", 1609.344),
    "yard": ("length", 0.9144), "yards": ("length", 0.9144),
    "foot": ("length", 0.3048), "feet": ("length", 0.3048), "ft": ("length", 0.3048),
    "inch": ("length", 0.0254), "inches": ("length", 0.0254), "in": ("length", 0.0254),
    # weight → kg
    "kg": ("weight", 1.0), "kilogram": ("weight", 1.0), "kilograms": ("weight", 1.0),
    "g": ("weight", 0.001), "gram": ("weight", 0.001), "grams": ("weight", 0.001),
    "lb": ("weight", 0.453592), "lbs": ("weight", 0.453592), "pound": ("weight", 0.453592), "pounds": ("weight", 0.453592),
    "oz": ("weight", 0.0283495), "ounce": ("weight", 0.0283495), "ounces": ("weight", 0.0283495),
    # temperature handled separately
    "c": ("temp", 1.0), "celsius": ("temp", 1.0),
    "f": ("temp", 1.0), "fahrenheit": ("temp", 1.0),
    "k": ("temp", 1.0), "kelvin": ("temp", 1.0),
    # data → bytes
    "b": ("data", 1.0), "byte": ("data", 1.0), "bytes": ("data", 1.0),
    "kb": ("data", 1024.0), "kilobyte": ("data", 1024.0), "kilobytes": ("data", 1024.0),
    "mb": ("data", 1024.0**2), "megabyte": ("data", 1024.0**2), "megabytes": ("data", 1024.0**2),
    "gb": ("data", 1024.0**3), "gigabyte": ("data", 1024.0**3), "gigabytes": ("data", 1024.0**3),
    "tb": ("data", 1024.0**4), "terabyte": ("data", 1024.0**4), "terabytes": ("data", 1024.0**4),
}


def _convert_temp(value: float, from_unit: str, to_unit: str) -> float:
    # normalise to Celsius
    if from_unit in ("f", "fahrenheit"):
        c = (value - 32) * 5 / 9
    elif from_unit in ("k", "kelvin"):
        c = value - 273.15
    else:
        c = value
    # convert from Celsius to target
    if to_unit in ("f", "fahrenheit"):
        return c * 9 / 5 + 32
    elif to_unit in ("k", "kelvin"):
        return c + 273.15
    return c


def convert_units(value: str, from_unit: str, to_unit: str, **_) -> str:
    try:
        v = float(value)
    except ValueError:
        return f"✗ Invalid number: {value}"

    fu = from_unit.lower().strip()
    tu = to_unit.lower().strip()

    from_info = _UNIT_TABLE.get(fu)
    to_info = _UNIT_TABLE.get(tu)

    if from_info is None:
        return f"✗ Unknown unit: {from_unit}"
    if to_info is None:
        return f"✗ Unknown unit: {to_unit}"

    from_type, _ = from_info
    to_type, _ = to_info

    if from_type != to_type:
        return f"✗ Cannot convert {from_type} to {to_type}."

    if from_type == "temp":
        result = _convert_temp(v, fu, tu)
    else:
        _, from_factor = from_info
        _, to_factor = to_info
        result = v * from_factor / to_factor

    return f"{v} {from_unit} = {result:.6g} {to_unit}"


# ══════════════════════════════════════════════════════════════════════════════
# Trivia & Jokes
# ══════════════════════════════════════════════════════════════════════════════

def tell_trivia(**_) -> str:
    return random.choice(_TRIVIA)


def tell_joke(**_) -> str:
    settings = cfg.load_settings()
    pool = list(_JOKES_CLEAN)
    if settings.get("dark_jokes", True):
        pool += _JOKES_DARK
    return random.choice(pool)


# ══════════════════════════════════════════════════════════════════════════════
# Registration
# ══════════════════════════════════════════════════════════════════════════════

def register_commands(registry: CommandRegistry, scheduler=None) -> None:
    registry.register_all([
        make_command("get_weather", get_weather, "Show weather for a city",
                     aliases=["weather"],
                     args_help="[city]", category="Information"),
        make_command("set_api_key", set_api_key, "Save your OpenWeatherMap API key",
                     aliases=["set weather api key"],
                     args_help="<key>", category="Information"),
        make_command("define_word", define_word, "Define a word",
                     aliases=["define", "definition", "meaning of"],
                     args_help="<word>", category="Information"),
        make_command("calculate", calculate, "Evaluate a math expression",
                     aliases=["calc", "math", "compute"],
                     args_help="<expression>", category="Information"),
        make_command("convert_units", convert_units, "Convert between units",
                     aliases=["convert"],
                     args_help="<value> <from> to <to>", category="Information"),
        make_command("tell_trivia", tell_trivia, "Share a random fun fact",
                     aliases=["trivia", "fun fact", "fact"],
                     category="Information"),
        make_command("tell_joke", tell_joke, "Tell a joke",
                     aliases=["joke", "tell me a joke"],
                     category="Information"),
    ])
