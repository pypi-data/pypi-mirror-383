> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelSave/en.md)

The ModelSave node saves trained or modified models to your computer's storage. It takes a model as input and writes it to a file with your specified filename. This allows you to preserve your work and reuse models in future projects.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to be saved to disk |
| `filename_prefix` | STRING | Yes | - | The filename and path prefix for the saved model file (default: "diffusion_models/ComfyUI") |
| `prompt` | PROMPT | No | - | Workflow prompt information (automatically provided) |
| `extra_pnginfo` | EXTRA_PNGINFO | No | - | Additional workflow metadata (automatically provided) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| *None* | - | This node does not return any output values |
