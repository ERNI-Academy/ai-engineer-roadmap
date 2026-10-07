# Roadmap AI Engineer · ERNI

Guía del alumno del programa AI Engineer de ERNI: diagnóstico de entrada, rutas por perfil, cursos enlazados, entregas y calendario.

**Web:** https://infantesromeroadrian.github.io/ai-engineer-roadmap/

## Mantenimiento

Las páginas HTML (`index.html`, `ruta.html`, `conceptos.html`, `bloques.html`, `caso-final.html` y `evaluacion.html`) se generan a partir de la guía interna del programa. No se editan a mano: se cambia la guía y se vuelven a generar.

Después de ejecutar el generador interno, desde la raíz del repositorio se aplica la cabecera con el logo oficial:

```sh
python3 scripts/apply_branding.py
```

Este paso no requiere dependencias adicionales, valida las seis páginas antes de escribir y puede repetirse sin duplicar el logo ni sus estilos. Si cambia la estructura de cabecera del generador, el script lo indica para adaptar las sustituciones.

`assets/erni-logo.png` conserva los bytes del [logo oficial de ERNI](https://www.betterask.erni/wp-content/uploads/2023/09/ERNI_logo_color-768x199.png) (768 × 199 píxeles). La cabecera mantiene sus colores y proporción sobre fondo blanco, también en modo oscuro.
