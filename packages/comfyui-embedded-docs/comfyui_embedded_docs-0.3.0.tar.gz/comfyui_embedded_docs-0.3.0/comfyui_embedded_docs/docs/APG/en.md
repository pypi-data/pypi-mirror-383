> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/APG/en.md)

The APG (Adaptive Projected Guidance) node modifies the sampling process by adjusting how guidance is applied during diffusion. It separates the guidance vector into parallel and orthogonal components relative to the conditional output, allowing for more controlled image generation. The node provides parameters to scale the guidance, normalize its magnitude, and apply momentum for smoother transitions between diffusion steps.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | Required | - | - | The diffusion model to apply adaptive projected guidance to |
| `eta` | FLOAT | Required | 1.0 | -10.0 to 10.0 | Controls the scale of the parallel guidance vector. Default CFG behavior at a setting of 1. |
| `norm_threshold` | FLOAT | Required | 5.0 | 0.0 to 50.0 | Normalize guidance vector to this value, normalization disable at a setting of 0. |
| `momentum` | FLOAT | Required | 0.0 | -5.0 to 1.0 | Controls a running average of guidance during diffusion, disabled at a setting of 0. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | Returns the modified model with adaptive projected guidance applied to its sampling process |
