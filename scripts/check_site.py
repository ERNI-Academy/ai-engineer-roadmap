"""Comprueba enlaces locales, anclas y contratos de la web publicada."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build import PAGE_SLUGS, REDIRECTS, build_site


LOGO_SHA256 = "9c9d4aaf55ad8e2033fa4bd2a44955b7710bd2ac19afb0d5fe812f738c98d973"
PRIVATE_REFERENCE = re.compile(r"/home/|/Users/|obsidian://|teams\.microsoft\.com|loop\.microsoft\.com|air-vault", re.I)
# Material de apoyo: el texto visible no puede reintroducir el plan propio retirado.
FORBIDDEN_CASE_SENSITIVE = re.compile(r"\bD0\b|\b[BCEN](?:0[1-9]|1[0-9]|2[0-5])\b|\bTeams\b|\bEnric\b|\bDoR\b")
FORBIDDEN_CASE_INSENSITIVE = re.compile(
    r"mentor|entrega|Expediente Claro|20 semanas|160 h\b|diagnóstico|nivelación|convalid|acredit|SharePoint|loop\.cloud|Definition of Done",
    re.I,
)
COST_FIGURE = re.compile(r"\d\s*(?:€|EUR\b|USD\b|\$)|[€$]\s*\d|\bUSD\s*\d|\bEUR\s*\d|\d\s*euros?\b|\d\s*dólares\b|/\s*mes\b", re.I)
ROBOTS = re.compile(r'<meta name="robots" content="noindex">')



class VisibleText(HTMLParser):
    """Texto que ve o escucha quien visita la página, más sus atributos descriptivos."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self.hidden += 1
        attributes = dict(attrs)
        if tag == "meta":
            if attributes.get("name") == "description" and attributes.get("content"):
                self.parts.append(attributes["content"])
            return
        for name in ("alt", "title", "aria-label"):
            if value := attributes.get(name):
                self.parts.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style") and self.hidden:
            self.hidden -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def visible_text(document: str) -> str:
    parser = VisibleText()
    parser.feed(document)
    return " ".join(parser.parts)


def forbidden_terms(document: str) -> list[str]:
    """Devuelve las coincidencias prohibidas del texto visible, sin duplicados."""
    text = visible_text(document)
    found = [m.group(0) for m in FORBIDDEN_CASE_SENSITIVE.finditer(text)]
    found += [m.group(0) for m in FORBIDDEN_CASE_INSENSITIVE.finditer(text)]
    found += [m.group(0) for m in COST_FIGURE.finditer(text)]
    return sorted(set(found))


class PageLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[str] = []
        self.checkboxes: list[str] = []
        self.active_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if identifier := attributes.get("id"):
            self.ids.append(identifier)
        for name in ("href", "src"):
            if link := attributes.get(name):
                self.links.append(link)
        if srcset := attributes.get("srcset"):
            self.links.extend(entry.strip().split()[0] for entry in srcset.split(","))
        if tag == "input" and attributes.get("type") == "checkbox":
            self.checkboxes.append(attributes.get("id", ""))
        if tag == "a" and attributes.get("aria-current") == "page":
            self.active_links.append(attributes.get("href", ""))


def check_site(project_root: Path) -> list[str]:
    errors: list[str] = []
    documents: dict[str, PageLinks] = {}
    content: dict[str, str] = {}
    for slug in (*PAGE_SLUGS, *REDIRECTS):
        name = f"{slug}.html"
        content[name] = (project_root / name).read_text(encoding="utf-8")
        page = PageLinks()
        page.feed(content[name])
        documents[name] = page
        if duplicates := [identifier for identifier, count in Counter(page.ids).items() if count > 1]:
            errors.append(f"{name}: IDs duplicados: {', '.join(duplicates)}")
        if slug in PAGE_SLUGS and page.active_links != [name]:
            errors.append(f"{name}: sección activa incorrecta.")
        if terms := forbidden_terms(content[name]):
            errors.append(f"{name}: texto visible con contenido retirado del plan propio: {', '.join(terms)}")

    for name, page in documents.items():
        for link in page.links:
            target = urlsplit(link)
            if target.scheme or target.netloc:
                continue
            target_name = unquote(target.path) or name
            path = project_root / target_name
            if not path.is_file():
                errors.append(f"{name}: destino local inexistente: {link}")
            elif target.fragment and target_name in documents:
                if unquote(target.fragment) not in documents[target_name].ids:
                    errors.append(f"{name}: ancla inexistente: {link}")

    for slug, target in REDIRECTS.items():
        name = f"{slug}.html"
        if f'http-equiv="refresh" content="0; url={target}"' not in content[name] or not ROBOTS.search(content[name]):
            errors.append(f"{name}: debe ser una redirección a {target} con noindex.")
        if f'href="{target}"' not in content[name]:
            errors.append(f"{name}: falta el enlace visible a {target}.")
        if any(f'href="{name}"' in content[other] for other in content if other != name):
            errors.append(f"{name}: no debe enlazarse desde ninguna página.")

    if len(documents["index.html"].checkboxes) != 6:
        errors.append("La checklist de Inicio debe tener 6 casillas, una por paso del plan oficial.")
    if any(documents[f"{slug}.html"].checkboxes for slug in PAGE_SLUGS if slug != "index"):
        errors.append("Solo Inicio debe contener casillas de progreso.")
    if hashlib.sha256((project_root / "assets/erni-logo.png").read_bytes()).hexdigest() != LOGO_SHA256:
        errors.append("Los bytes del logo oficial han cambiado.")
    if len(re.findall(r'<section class="sec block">', content["bloques.html"])) != 10:
        errors.append("Deben conservarse los diez temas técnicos.")
    for required in ("mandan las slides", "v0.4 · 15 de octubre de 2026 · Material de apoyo del programa AI Engineer"):
        if required not in content["index.html"]:
            errors.append(f"Inicio: falta «{required}».")
    for path in (project_root / "source").rglob("*"):
        if path.is_file() and PRIVATE_REFERENCE.search(path.read_text(encoding="utf-8")):
            errors.append(f"Referencia privada en {path.relative_to(project_root)}.")
    return errors


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    try:
        errors = check_site(project_root)
        if build_site(project_root, check=True):
            errors.append("Hay deriva entre las fuentes y la web: ejecuta scripts/build.py.")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"No se pudo comprobar la web: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("OK: generación, enlaces y anclas locales, redirecciones, texto visible, 10 temas, checklist de 6 casillas y logo.")
    print("El filtro de referencias privadas es acotado; no sustituye la revisión de publicación.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
