> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelComputeDtype/en.md)

The ModelComputeDtype node allows you to change the computational data type used by a model during inference. It creates a copy of the input model and applies the specified data type setting, which can help optimize memory usage and performance depending on your hardware capabilities. This is particularly useful for debugging and testing different precision settings.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The input model to modify with a new compute data type |
| `dtype` | STRING | Yes | "default"<br>"fp32"<br>"fp16"<br>"bf16" | The computational data type to apply to the model |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with the new compute data type applied |
