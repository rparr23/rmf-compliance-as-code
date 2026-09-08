"""Artifact generators."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .categorization import categorize
from .poam import summarize_poam


def _env(template_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
    )


def generate_ssp(system: dict, template_dir: Path) -> str:
    c = system["categorization"]
    result = categorize(c["confidentiality"], c["integrity"], c["availability"])
    return _env(template_dir).get_template("ssp.md.j2").render(system=system, categorization=result)


def generate_poam(poam: dict, template_dir: Path) -> str:
    return (
        _env(template_dir)
        .get_template("poam.md.j2")
        .render(poam=poam, summary=summarize_poam(poam))
    )
