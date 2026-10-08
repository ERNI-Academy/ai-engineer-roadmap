"""Comprueba enlaces locales, anclas y contratos de la web publicada."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build import PAGE_SLUGS, build_site


LOGO_SHA256 = "9c9d4aaf55ad8e2033fa4bd2a44955b7710bd2ac19afb0d5fe812f738c98d973"
PRIVATE_REFERENCE = re.compile(r"/home/|/Users/|obsidian://|teams\.microsoft\.com|loop\.microsoft\.com|air-vault", re.I)


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
    for slug in PAGE_SLUGS:
        name = f"{slug}.html"
        content[name] = (project_root / name).read_text(encoding="utf-8")
        page = PageLinks()
        page.feed(content[name])
        documents[name] = page
        if duplicates := [identifier for identifier, count in Counter(page.ids).items() if count > 1]:
            errors.append(f"{name}: IDs duplicados: {', '.join(duplicates)}")
        if page.active_links != [name]:
            errors.append(f"{name}: sección activa incorrecta.")

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

    if len(documents["evaluacion.html"].checkboxes) != 15:
        errors.append("La checklist debe conservar sus 15 casillas.")
    if hashlib.sha256((project_root / "assets/erni-logo.png").read_bytes()).hexdigest() != LOGO_SHA256:
        errors.append("Los bytes del logo oficial han cambiado.")
    if len(re.findall(r'id="b\d{2}-', content["bloques.html"])) != 10:
        errors.append("Deben conservarse los diez bloques B01–B10.")
    course_ids = set(re.findall(r"\bC(\d{2})\b", content["bloques.html"]))
    if course_ids != {f"{number:02}" for number in range(1, 26)}:
        errors.append("Deben conservarse los cursos C01–C25.")
    for old_claim in ("150 a 400", "150 € cada", "30 €/mes durante 2 meses", "2 capítulos gratis", "4 meses de programa central", "Versión 0.2"):
        if any(old_claim in document for document in content.values()):
            errors.append(f"Persiste una afirmación retirada: {old_claim}")
    for required in ("85 EUR", "256 EUR", "29 USD/mes", "156 h de base + 4 h de margen"):
        if required not in content["index.html"]:
            errors.append(f"Inicio: falta la referencia {required}.")
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
    print("OK: generación, enlaces y anclas locales, 25 cursos, 10 bloques, costes, checklist y logo.")
    print("El filtro de referencias privadas es acotado; no sustituye la revisión de publicación.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
