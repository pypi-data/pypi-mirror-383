> Esta documentación fue generada por IA. Si encuentra algún error o tiene sugerencias de mejora, ¡no dude en contribuir! [Editar en GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/HyperTile/es.md)

El nodo HyperTile aplica una técnica de mosaico al mecanismo de atención en los modelos de difusión para optimizar el uso de memoria durante la generación de imágenes. Divide el espacio latente en mosaicos más pequeños y los procesa por separado, luego reensambla los resultados. Esto permite trabajar con tamaños de imagen más grandes sin quedarse sin memoria.

## Entradas

| Parámetro | Tipo de Dato | Requerido | Rango | Descripción |
|-----------|-----------|----------|-------|-------------|
| `modelo` | MODEL | Sí | - | El modelo de difusión al que aplicar la optimización HyperTile |
| `tamaño_de_mosaico` | INT | No | 1-2048 | El tamaño objetivo del mosaico para el procesamiento (por defecto: 256) |
| `tamaño_de_intercambio` | INT | No | 1-128 | Controla cómo se reorganizan los mosaicos durante el procesamiento (por defecto: 2) |
| `profundidad_máxima` | INT | No | 0-10 | Nivel máximo de profundidad para aplicar el mosaico (por defecto: 0) |
| `escala_de_profundidad` | BOOLEAN | No | - | Si escalar el tamaño del mosaico basándose en el nivel de profundidad (por defecto: False) |

## Salidas

| Nombre de Salida | Tipo de Dato | Descripción |
|-------------|-----------|-------------|
| `modelo` | MODEL | El modelo modificado con la optimización HyperTile aplicada |
