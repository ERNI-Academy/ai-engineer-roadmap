"""Genera la web desde sus fuentes públicas, sin servicios ni dependencias."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path


PAGE_SLUGS = ("index", "ruta", "conceptos", "bloques")
# Páginas retiradas: se publican solo como redirección para no romper enlaces antiguos.
REDIRECTS = {"caso-final": "index.html", "evaluacion": "index.html"}
PAGE_FIELDS = frozenset(("slug", "title", "description", "body_class", "nav_label"))
TEMPLATE_FIELDS = frozenset(("title", "description", "body_class", "navigation", "content"))
REDIRECT_FIELDS = frozenset(("target",))
TOKEN = re.compile(r"\{\{([a-z_]+)\}\}")


def read_pages(source: Path) -> list[dict[str, str]]:
    pages = json.loads((source / "pages.json").read_text(encoding="utf-8"))
    if not isinstance(pages, list) or len(pages) != len(PAGE_SLUGS):
        raise ValueError("source/pages.json debe definir las cuatro páginas públicas.")
    for page in pages:
        if not isinstance(page, dict) or page.keys() != PAGE_FIELDS:
            raise ValueError("Metadatos de página incompletos o desconocidos.")
        if not all(isinstance(value, str) and value.strip() for value in page.values()):
            raise ValueError("Los metadatos deben ser textos no vacíos.")
    if tuple(page["slug"] for page in pages) != PAGE_SLUGS:
        raise ValueError("Las URLs y el orden de las cuatro páginas deben conservarse.")
    return pages


def render_site(project_root: Path) -> dict[str, bytes]:
    """Valida las fuentes y devuelve todos los outputs antes de escribir nada."""
    source = project_root / "source"
    pages = read_pages(source)
    template = (source / "template.html").read_text(encoding="utf-8")
    if set(TOKEN.findall(template)) != TEMPLATE_FIELDS:
        raise ValueError("source/template.html contiene marcadores incompatibles.")
    redirect = (source / "redirect.html").read_text(encoding="utf-8")
    if set(TOKEN.findall(redirect)) != REDIRECT_FIELDS:
        raise ValueError("source/redirect.html contiene marcadores incompatibles.")
    outputs: dict[str, bytes] = {}

    for page in pages:
        navigation = []
        for entry in pages:
            current = ' aria-current="page"' if entry["slug"] == page["slug"] else ""
            navigation.append(
                f'<a href="{entry["slug"]}.html"{current}>'
                f'{html.escape(entry["nav_label"])}</a>'
            )
        content = (source / "pages" / f'{page["slug"]}.html').read_text(encoding="utf-8")
        if TOKEN.search(content):
            raise ValueError(f'{page["slug"]}: marcador de contenido sin resolver.')
        fields = {key: html.escape(page[key], quote=True) for key in ("title", "description", "body_class")}
        fields.update(navigation="\n".join(navigation), content=content.rstrip())
        rendered = TOKEN.sub(lambda match: fields[match.group(1)], template)
        outputs[f'{page["slug"]}.html'] = rendered.encode("utf-8")
    for slug, target in REDIRECTS.items():
        if Path(target).stem not in PAGE_SLUGS:
            raise ValueError(f"La redirección {slug} apunta a un destino inexistente.")
        outputs[f"{slug}.html"] = TOKEN.sub(lambda _: html.escape(target, quote=True), redirect).encode("utf-8")
    return outputs


def build_site(project_root: Path, *, check: bool = False) -> tuple[str, ...]:
    outputs = render_site(project_root)
    changed = tuple(
        name for name, content in outputs.items()
        if not (project_root / name).is_file() or (project_root / name).read_bytes() != content
    )
    if not check:
        for name in changed:
            output = project_root / name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(outputs[name])
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Detecta deriva sin escribir archivos.")
    args = parser.parse_args(argv)
    try:
        changed = build_site(Path(__file__).resolve().parent.parent, check=args.check)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"No se pudo generar la web: {exc}", file=sys.stderr)
        return 1
    if args.check and changed:
        print("HTML desactualizado: " + ", ".join(changed), file=sys.stderr)
        print("Ejecuta python3 scripts/build.py y revisa el diff.", file=sys.stderr)
        return 1
    print(f"Generación comprobada: {len(PAGE_SLUGS)} páginas y {len(REDIRECTS)} redirecciones; "
          f"{len(changed)} archivos actualizados." if not args.check else "Sin deriva: web y fuentes coinciden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
