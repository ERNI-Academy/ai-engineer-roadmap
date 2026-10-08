# Roadmap AI Engineer · ERNI

Guía del alumno del programa AI Engineer de ERNI: diagnóstico de entrada, rutas por perfil, cursos enlazados, entregas y calendario. **Versión 0.3 · 8 de octubre de 2026 · Propuesta para revisión de ERNI.**

**Web:** https://erni-academy.github.io/ai-engineer-roadmap/

## Fuentes y generación

Este repositorio contiene todas las fuentes necesarias para reproducir las seis páginas. `source/pages/*.html` son los fragmentos de contenido extraídos de la web pública anterior; no requieren documentación interna. Se conserva el orden de los 25 cursos, los diez bloques, las URLs y las anclas existentes.

- `source/template.html`: cabecera, navegación y pie comunes.
- `source/pages.json`: títulos, descripciones y orden de navegación.
- `source/pages/*.html`: contenido por página. Editar aquí, no los HTML de la raíz.
- `source/seguimiento-semanal.md`: plantilla única para la vista legible y la descarga.
- `assets/site.css` y `assets/site.js`: estilos e interacciones compartidos.
- `diagrams/`: diagramas públicos existentes; el generador no los transforma.

Requiere **Python 3.10 o posterior**, solo biblioteca estándar. Desde la raíz:

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m http.server 8000 --bind 127.0.0.1
```

Abre `http://127.0.0.1:8000/`. La generación valida todas las fuentes antes de escribir; no depende de red, reloj ni rutas externas. Repetirla no cambia los archivos. `--check` devuelve código 1 si falta una salida o hay deriva y no escribe nada. Incluye en la publicación los seis HTML, `assets/`, `downloads/` y `diagrams/`. Se retira el antiguo paso `apply_branding.py`: el logo ya forma parte de la plantilla común.

## Comprobaciones

```sh
python3 -B scripts/check_site.py
python3 -B -m unittest discover -s tests -p 'test_*.py'
node --test tests/test_interactions.cjs
```

La última comprobación necesita Node.js 18 o posterior y no instala paquetes. Comprueba persistencia/reinicio de casillas, errores de almacenamiento, datos locales inválidos, copia y desplazamiento de navegación mediante dobles sintéticos. Las comprobaciones Python cubren generación determinista, ausencia de escrituras de `--check`, errores de fuentes, enlaces/anclas locales, logo, cursos, bloques y regresiones de contenido. El filtro acotado de referencias privadas no acredita por sí solo ausencia de información sensible.

Antes de publicar, revisar también en navegador a 1440, 390 y 320 px, modo claro/oscuro, teclado y sin JavaScript: sección activa visible, ausencia de desbordamiento de página, recarga de casillas, copia/descarga y legibilidad. Las pruebas con dobles no sustituyen esa comprobación; los enlaces externos y la experiencia dentro de cursos no se validan automáticamente.

## Seguimiento y límites

Las 15 casillas guardan únicamente booleanos en `localStorage`, bajo `erni.ai-engineer-roadmap.v0.3.checklist`. No hay backend, envío, analítica ni sincronización entre dispositivos. Los datos incompatibles o un almacenamiento bloqueado dejan la checklist operativa durante la visita con un aviso. Reiniciar requiere confirmación local; no cambia la evaluación del mentor. Borrar datos del navegador elimina el seguimiento y cambiar de versión de clave empieza un registro nuevo.

Sin JavaScript se mantienen navegación, contenido, casillas temporales y descarga de la plantilla Markdown. El botón de copia necesita permiso de portapapeles; si falla, la plantilla se puede seleccionar o descargar. No se recogen nombres ni texto libre.

La referencia del programa es **20 semanas a 8 h: 160 h, con 156 h de base y 4 h de margen**. La nivelación y la certificación opcional son aparte. Los costes públicos incluyen fecha y fuente; las licencias corporativas, los meses autorizados y el consumo siguen pendientes, por lo que no se publica un total cerrado. Esta web es una propuesta didáctica, no una aprobación corporativa.

`assets/erni-logo.png` conserva los bytes del [logo oficial de ERNI](https://www.betterask.erni/wp-content/uploads/2023/09/ERNI_logo_color-768x199.png) (768 × 199 píxeles). La cabecera mantiene sus colores y proporción sobre fondo blanco, también en modo oscuro.
