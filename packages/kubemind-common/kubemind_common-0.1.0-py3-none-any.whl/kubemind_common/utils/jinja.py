from __future__ import annotations

from jinja2 import Environment, StrictUndefined


def create_jinja_env() -> Environment:
    env = Environment(undefined=StrictUndefined, autoescape=False)
    return env

