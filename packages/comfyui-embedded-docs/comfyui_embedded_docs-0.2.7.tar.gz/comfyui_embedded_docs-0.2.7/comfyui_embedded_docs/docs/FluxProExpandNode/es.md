> Esta documentación fue generada por IA. Si encuentra algún error o tiene sugerencias de mejora, ¡no dude en contribuir! [Editar en GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FluxProExpandNode/es.md)

Expande imágenes basándose en un prompt. Este nodo expande una imagen añadiendo píxeles en los lados superior, inferior, izquierdo y derecho, mientras genera nuevo contenido que coincide con la descripción de texto proporcionada.

## Entradas

| Parámetro | Tipo de Dato | Requerido | Rango | Descripción |
|-----------|-----------|----------|-------|-------------|
| `imagen` | IMAGE | Sí | - | La imagen de entrada que se va a expandir |
| `prompt` | STRING | No | - | Prompt para la generación de la imagen (valor por defecto: "") |
| `reescaleado de prompt` | BOOLEAN | No | - | Si se debe realizar un remuestreo del prompt. Si está activo, modifica automáticamente el prompt para una generación más creativa, pero los resultados son no deterministas (la misma semilla no producirá exactamente el mismo resultado). (valor por defecto: False) |
| `arriba` | INT | No | 0-2048 | Número de píxeles a expandir en la parte superior de la imagen (valor por defecto: 0) |
| `abajo` | INT | No | 0-2048 | Número de píxeles a expandir en la parte inferior de la imagen (valor por defecto: 0) |
| `izquierda` | INT | No | 0-2048 | Número de píxeles a expandir en el lado izquierdo de la imagen (valor por defecto: 0) |
| `derecha` | INT | No | 0-2048 | Número de píxeles a expandir en el lado derecho de la imagen (valor por defecto: 0) |
| `guía` | FLOAT | No | 1.5-100 | Fuerza de guía para el proceso de generación de imágenes (valor por defecto: 60) |
| `pasos` | INT | No | 15-50 | Número de pasos para el proceso de generación de imágenes (valor por defecto: 50) |
| `semilla` | INT | No | 0-18446744073709551615 | La semilla aleatoria utilizada para crear el ruido. (valor por defecto: 0) |

## Salidas

| Nombre de Salida | Tipo de Dato | Descripción |
|-------------|-----------|-------------|
| `imagen` | IMAGE | La imagen de salida expandida |
