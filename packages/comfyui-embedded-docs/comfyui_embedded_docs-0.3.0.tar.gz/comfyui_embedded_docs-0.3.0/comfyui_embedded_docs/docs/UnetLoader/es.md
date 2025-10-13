
El nodo UNETLoader está diseñado para cargar modelos U-Net por nombre, facilitando el uso de arquitecturas U-Net preentrenadas dentro del sistema.

Este nodo detectará los modelos ubicados en la carpeta `ComfyUI/models/diffusion_models`.

## Entradas

| Parámetro   | Tipo de Dato | Descripción |
|-------------|--------------|-------------|
| `nombre_unet` | COMBO[STRING] | Especifica el nombre del modelo U-Net que se va a cargar. Este nombre se utiliza para localizar el modelo dentro de una estructura de directorio predefinida, permitiendo la carga dinámica de diferentes modelos U-Net. |
| `tipo_dato_peso` | ... | 🚧  fp8_e4m3fn fp9_e5m2  |

## Salidas

| Parámetro | Tipo de Dato | Descripción |
|-----------|-------------|-------------|
| `model`   | MODEL     | Devuelve el modelo U-Net cargado, permitiendo su utilización para procesamiento adicional o inferencia dentro del sistema. |
