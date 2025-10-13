> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/DifferentialDiffusion/en.md)

The Differential Diffusion node modifies the denoising process by applying a binary mask based on timestep thresholds. It creates a mask that blends between the original denoise mask and a threshold-based binary mask, allowing controlled adjustment of the diffusion process strength.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The diffusion model to modify |
| `strength` | FLOAT | No | 0.0 - 1.0 | Controls the blending strength between the original denoise mask and the binary threshold mask (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified diffusion model with updated denoise mask function |
