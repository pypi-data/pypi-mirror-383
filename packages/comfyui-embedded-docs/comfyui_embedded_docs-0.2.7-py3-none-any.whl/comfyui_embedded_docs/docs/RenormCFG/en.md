> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RenormCFG/en.md)

The RenormCFG node modifies the classifier-free guidance (CFG) process in diffusion models by applying conditional scaling and normalization. It adjusts the denoising process based on specified timestep thresholds and renormalization factors to control the influence of conditional versus unconditional predictions during image generation.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The diffusion model to apply renormalized CFG to |
| `cfg_trunc` | FLOAT | No | 0.0 - 100.0 | Timestep threshold for applying CFG scaling (default: 100.0) |
| `renorm_cfg` | FLOAT | No | 0.0 - 100.0 | Renormalization factor for controlling conditional guidance strength (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with renormalized CFG function applied |
