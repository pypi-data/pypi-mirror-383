> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TomePatchModel/en.md)

The TomePatchModel node applies Token Merging (ToMe) to a diffusion model to reduce computational requirements during inference. It works by selectively merging similar tokens in the attention mechanism, allowing the model to process fewer tokens while maintaining image quality. This technique helps speed up generation without significant quality loss.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The diffusion model to apply token merging to |
| `ratio` | FLOAT | No | 0.0 - 1.0 | The ratio of tokens to merge (default: 0.3) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with token merging applied |
