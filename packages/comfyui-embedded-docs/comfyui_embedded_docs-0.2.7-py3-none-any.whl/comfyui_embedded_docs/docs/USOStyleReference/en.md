> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/USOStyleReference/en.md)

The USOStyleReference node applies style reference patches to models using encoded image features from CLIP vision output. It creates a modified version of the input model by incorporating style information extracted from visual inputs, enabling style transfer or reference-based generation capabilities.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The base model to apply the style reference patch to |
| `model_patch` | MODEL_PATCH | Yes | - | The model patch containing style reference information |
| `clip_vision_output` | CLIP_VISION_OUTPUT | Yes | - | The encoded visual features extracted from CLIP vision processing |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with applied style reference patches |
