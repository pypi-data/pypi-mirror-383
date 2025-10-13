> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelSamplingFlux/en.md)

The ModelSamplingFlux node applies Flux model sampling to a given model by calculating a shift parameter based on image dimensions. It creates a specialized sampling configuration that adjusts the model's behavior according to the specified width, height, and shift parameters, then returns the modified model with the new sampling settings applied.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply Flux sampling to |
| `max_shift` | FLOAT | Yes | 0.0 - 100.0 | Maximum shift value for sampling calculation (default: 1.15) |
| `base_shift` | FLOAT | Yes | 0.0 - 100.0 | Base shift value for sampling calculation (default: 0.5) |
| `width` | INT | Yes | 16 - MAX_RESOLUTION | Width of the target image in pixels (default: 1024) |
| `height` | INT | Yes | 16 - MAX_RESOLUTION | Height of the target image in pixels (default: 1024) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with Flux sampling configuration applied |
