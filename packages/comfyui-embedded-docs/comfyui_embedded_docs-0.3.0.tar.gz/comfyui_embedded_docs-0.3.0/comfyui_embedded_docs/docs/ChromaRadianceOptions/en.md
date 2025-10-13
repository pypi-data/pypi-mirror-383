> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ChromaRadianceOptions/en.md)

The ChromaRadianceOptions node allows you to configure advanced settings for the Chroma Radiance model. It wraps an existing model and applies specific options during the denoising process based on sigma values, enabling fine-tuned control over NeRF tile size and other radiance-related parameters.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | Required | - | - | The model to apply Chroma Radiance options to |
| `preserve_wrapper` | BOOLEAN | Optional | True | - | When enabled, will delegate to an existing model function wrapper if it exists. Generally should be left enabled. |
| `start_sigma` | FLOAT | Optional | 1.0 | 0.0 - 1.0 | First sigma that these options will be in effect. |
| `end_sigma` | FLOAT | Optional | 0.0 | 0.0 - 1.0 | Last sigma that these options will be in effect. |
| `nerf_tile_size` | INT | Optional | -1 | -1 and above | Allows overriding the default NeRF tile size. -1 means use the default (32). 0 means use non-tiling mode (may require a lot of VRAM). |

**Note:** The Chroma Radiance options only take effect when the current sigma value falls between `end_sigma` and `start_sigma` (inclusive). The `nerf_tile_size` parameter is only applied when set to 0 or higher values.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with Chroma Radiance options applied |
