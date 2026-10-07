"""Aplica la cabecera ERNI a las páginas producidas por el generador interno."""

from __future__ import annotations

import sys
from pathlib import Path


PAGES = (
    "index.html",
    "ruta.html",
    "conceptos.html",
    "bloques.html",
    "caso-final.html",
    "evaluacion.html",
)
ORIGINAL_HEADER = (
    '<a class="brand" href="index.html">'
    '<span class="brand-mark" aria-hidden="true">E</span>'
    '<span>ERNI · Roadmap AI Engineer</span></a>'
)
BRANDED_HEADER = (
    '<a class="brand" href="index.html"><span class="brand-logo">'
    '<img src="assets/erni-logo.png" alt="ERNI" width="768" height="199">'
    '</span><span>Roadmap AI Engineer</span></a>'
)
ORIGINAL_CSS = (
    ".brand-mark { display: grid; place-items: center; width: 28px; "
    "height: 28px; border-radius: 8px; background: var(--accent); "
    "color: #06202f; font-weight: 800; }"
)
BRANDED_CSS = """.brand-logo { display: inline-flex; flex: none; padding: 5px 8px; border-radius: 6px; background: #fff; }
.brand-logo img { display: block; width: 108px; height: auto; }
@media (max-width: 380px) {
  .brand { gap: 8px; font-size: 14px; }
  .brand-logo img { width: 92px; }
}"""


def replace_branding(
    content: str,
    original: str,
    branded: str,
    page_name: str,
    component: str,
) -> str:
    if content.count(original) + content.count(branded) != 1:
        raise ValueError(
            f"{page_name}: {component} incompatible. Regenera el HTML con el "
            "generador interno y comprueba su estructura antes de aplicar branding."
        )
    return content.replace(original, branded, 1)


def apply_branding(project_root: Path) -> int:
    logo_path = project_root / "assets" / "erni-logo.png"
    if not logo_path.is_file():
        raise ValueError(
            "Falta assets/erni-logo.png. Restaura el logo oficial antes de continuar."
        )
    if not logo_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("assets/erni-logo.png no es un PNG. Restaura el logo oficial.")

    updates: list[tuple[Path, bytes]] = []
    # Validar todo el lote evita transformar cinco páginas si la sexta cambió.
    for page_name in PAGES:
        page_path = project_root / page_name
        content = page_path.read_bytes().decode("utf-8")
        branded = replace_branding(
            content, ORIGINAL_HEADER, BRANDED_HEADER, page_name, "cabecera"
        )
        branded = replace_branding(
            branded, ORIGINAL_CSS, BRANDED_CSS, page_name, "CSS de cabecera"
        )
        if branded != content:
            updates.append((page_path, branded.encode("utf-8")))

    for page_path, content in updates:
        page_path.write_bytes(content)
    return len(updates)


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    try:
        updated = apply_branding(project_root)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"No se pudo aplicar branding: {exc}", file=sys.stderr)
        return 1
    if updated:
        print(f"Branding aplicado a {updated} páginas.")
    else:
        print("Branding ya aplicado; no hay cambios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
