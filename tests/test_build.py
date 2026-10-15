"""Regresiones del contrato de generación; solo biblioteca estándar."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build import build_site, render_site
from check_site import check_site, forbidden_terms


ROOT = Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        shutil.copytree(ROOT / "source", self.root / "source")

    def test_repeated_build_is_deterministic_and_preserves_file_mtimes(self) -> None:
        self.assertEqual(len(build_site(self.root)), 6)
        first = {name: (self.root / name).stat().st_mtime_ns for name in render_site(self.root)}
        self.assertEqual(build_site(self.root), ())
        self.assertEqual(first, {name: (self.root / name).stat().st_mtime_ns for name in first})

    def test_check_detects_drift_and_never_writes_or_creates_outputs(self) -> None:
        self.assertEqual(len(build_site(self.root, check=True)), 6)
        self.assertFalse((self.root / "index.html").exists())
        build_site(self.root)
        output = self.root / "index.html"
        output.write_text("derived output changed", encoding="utf-8")
        snapshot = (output.read_bytes(), output.stat().st_mtime_ns)
        self.assertEqual(build_site(self.root, check=True), ("index.html",))
        self.assertEqual(snapshot, (output.read_bytes(), output.stat().st_mtime_ns))

    def test_invalid_last_source_leaves_all_existing_outputs_untouched(self) -> None:
        build_site(self.root)
        snapshot = {name: (self.root / name).read_bytes() for name in render_site(self.root)}
        (self.root / "source/pages/bloques.html").write_text("{{unexpected}}", encoding="utf-8")
        with self.assertRaises(ValueError):
            build_site(self.root)
        self.assertEqual(snapshot, {name: (self.root / name).read_bytes() for name in snapshot})

    def test_metadata_cannot_change_public_urls_or_inject_markup(self) -> None:
        path = self.root / "source/pages.json"
        metadata = json.loads(path.read_text())
        metadata[0]["title"] = '<img src="unexpected">'
        path.write_text(json.dumps(metadata), encoding="utf-8")
        self.assertIn(b"&lt;img src=&quot;unexpected&quot;&gt;", render_site(self.root)["index.html"])
        metadata[0]["slug"] = "../unexpected"
        path.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaises(ValueError):
            render_site(self.root)

    def test_retired_pages_are_noindex_redirects_to_home(self) -> None:
        outputs = render_site(self.root)
        for name in ("caso-final.html", "evaluacion.html"):
            page = outputs[name].decode("utf-8")
            self.assertIn('http-equiv="refresh" content="0; url=index.html"', page)
            self.assertIn('<meta name="robots" content="noindex">', page)
            self.assertIn('<a href="index.html">Ir al inicio</a>', page)
        for name in ("index.html", "ruta.html", "conceptos.html", "bloques.html"):
            self.assertNotIn("caso-final.html", outputs[name].decode("utf-8"))
            self.assertNotIn("evaluacion.html", outputs[name].decode("utf-8"))

    def test_visible_text_filter_rejects_retired_plan_content(self) -> None:
        for text in ("Haz el D0", "Entrega E03", "Tu mentor", "20 semanas", "Expediente Claro", "Curso C07",
                     "Abre Teams", "40 €/mes", "29 USD/mes", "85 EUR", "diagnóstico", "convalidar", "Acreditar"):
            self.assertTrue(forbidden_terms(f"<p>{text}</p>"), text)
        self.assertTrue(forbidden_terms('<img alt="Ruta B01" src="x.png">'))
        self.assertEqual(forbidden_terms('<script>var B01 = "mentor";</script><p>Proyecto 1 y DataCamp</p>'), [])

    def test_current_site_contracts_and_links(self) -> None:
        self.assertEqual(check_site(ROOT), [])


if __name__ == "__main__":
    unittest.main()
