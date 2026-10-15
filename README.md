# Roadmap AI Engineer · ERNI

Material de apoyo técnico del programa AI Engineer de ERNI: el plan oficial en un vistazo, orientación por perfil, glosario de conceptos y temas técnicos con cursos opcionales. **v0.4 · 15 de octubre de 2026.**

**Web:** https://erni-academy.github.io/ai-engineer-roadmap/

La web **no define el plan**: el plan, los plazos y lo que hay que hacer están en las slides del kick-off. Si algo de la web no cuadra con ellas, mandan las slides. Por eso no contiene tareas evaluables, calendario propio, condiciones de avance ni cifras de coste.

## Estructura

| Página | Contenido |
|---|---|
| `index.html` · Inicio | El plan oficial en seis pasos, qué es un AI Engineer, stack típico, accesos, checklist personal de seis casillas y requisitos técnicos |
| `ruta.html` · Tu perfil | Qué te costará más o menos según tu perfil, rutas por perfil y refuerzos opcionales |
| `conceptos.html` · Conceptos | 22 conceptos con ejemplo, error típico y dónde te los encontrarás en el plan |
| `bloques.html` · Temas técnicos | Diez temas (por qué importan, qué conviene dominar, cursos opcionales) y consejos para los proyectos. Conserva el nombre de archivo para no romper enlaces |

`caso-final.html` y `evaluacion.html` ya no tienen contenido: se publican solo como **redirección** a `index.html` (`meta refresh` inmediato, enlace visible y `noindex`), fuera de la navegación, para no romper enlaces antiguos.

## Fuentes y generación

Las páginas HTML de la raíz se generan: se edita `source/`, nunca los HTML a mano.

- `source/template.html`: cabecera, navegación y pie comunes.
- `source/pages.json`: títulos, descripciones y orden de navegación de las cuatro páginas.
- `source/pages/*.html`: contenido de cada página.
- `source/redirect.html`: plantilla de las redirecciones. Las páginas redirigidas se declaran en `REDIRECTS` de `scripts/build.py`.
- `assets/site.css` y `assets/site.js`: estilos e interacciones compartidos.
- `diagrams/`: diagramas públicos; el generador no los transforma.

Requiere **Python 3.10 o posterior**, solo biblioteca estándar. Desde la raíz:

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m http.server 8000 --bind 127.0.0.1
```

Abre `http://127.0.0.1:8000/`. La generación valida todas las fuentes antes de escribir y repetirla no cambia los archivos. `--check` devuelve código 1 si falta una salida o hay deriva y no escribe nada. Se publican los seis HTML, `assets/` y `diagrams/`.

## Comprobaciones

```sh
python3 -B scripts/check_site.py
python3 -B -m unittest discover -s tests -p 'test_*.py'
node --test tests/test_interactions.cjs
```

- `check_site.py`: enlaces y anclas locales, redirecciones, logo, diez temas, checklist de seis casillas y ausencia de deriva. Falla si el **texto visible** publicado (incluidos `alt`, `title` y `aria-label`) reintroduce contenido del plan propio retirado (códigos, evaluación, nombres internos) o cifras de coste.
- `tests/test_build.py`: generación determinista, `--check` sin escrituras, redirecciones y filtro de texto visible.
- `tests/test_interactions.cjs` (Node.js 18 o posterior, sin paquetes): persistencia y reinicio de las casillas, errores de almacenamiento, datos locales inválidos y desplazamiento de la navegación, con dobles sintéticos.

Antes de publicar, revisar también en navegador a 1440, 390 y 320 px, en modo claro y oscuro, con teclado y sin JavaScript. Los enlaces externos no se validan automáticamente.

## Progreso personal

Las seis casillas de Inicio (una por paso del plan oficial) guardan solo booleanos en `localStorage`, bajo `erni.ai-engineer-roadmap.v0.4.checklist`. No hay backend, envío, analítica ni sincronización entre dispositivos. Con datos incompatibles o almacenamiento bloqueado, la checklist sigue funcionando durante la visita con un aviso. Borrar los datos del navegador elimina el progreso; cambiar la versión de la clave empieza un registro nuevo.

`assets/erni-logo.png` conserva los bytes del [logo oficial de ERNI](https://www.betterask.erni/wp-content/uploads/2023/09/ERNI_logo_color-768x199.png) (768 × 199 píxeles), sobre fondo blanco también en modo oscuro.
