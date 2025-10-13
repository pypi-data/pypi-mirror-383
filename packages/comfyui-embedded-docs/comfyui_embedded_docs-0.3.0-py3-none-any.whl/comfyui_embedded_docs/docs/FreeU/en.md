> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FreeU/en.md)

The FreeU node applies frequency-domain modifications to a model's output blocks to enhance image generation quality. It works by scaling different channel groups and applying Fourier filtering to specific feature maps, allowing for fine-tuned control over the model's behavior during the generation process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply FreeU modifications to |
| `b1` | FLOAT | Yes | 0.0 - 10.0 | Backbone scaling factor for model_channels × 4 features (default: 1.1) |
| `b2` | FLOAT | Yes | 0.0 - 10.0 | Backbone scaling factor for model_channels × 2 features (default: 1.2) |
| `s1` | FLOAT | Yes | 0.0 - 10.0 | Skip connection scaling factor for model_channels × 4 features (default: 0.9) |
| `s2` | FLOAT | Yes | 0.0 - 10.0 | Skip connection scaling factor for model_channels × 2 features (default: 0.2) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with FreeU patches applied |
