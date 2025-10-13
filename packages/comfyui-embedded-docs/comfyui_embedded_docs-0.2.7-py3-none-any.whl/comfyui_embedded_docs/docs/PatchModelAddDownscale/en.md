> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PatchModelAddDownscale/en.md)

The PatchModelAddDownscale node implements Kohya Deep Shrink functionality by applying downscaling and upscaling operations to specific blocks in a model. It reduces the resolution of intermediate features during processing and then restores them to their original size, which can improve performance while maintaining quality. The node allows precise control over when and how these scaling operations occur during the model's execution.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply the downscale patch to |
| `block_number` | INT | No | 1-32 | The specific block number where downscaling will be applied (default: 3) |
| `downscale_factor` | FLOAT | No | 0.1-9.0 | The factor by which to downscale the features (default: 2.0) |
| `start_percent` | FLOAT | No | 0.0-1.0 | The starting point in the denoising process where downscaling begins (default: 0.0) |
| `end_percent` | FLOAT | No | 0.0-1.0 | The ending point in the denoising process where downscaling stops (default: 0.35) |
| `downscale_after_skip` | BOOLEAN | No | - | Whether to apply downscaling after skip connections (default: True) |
| `downscale_method` | COMBO | No | "bicubic"<br>"nearest-exact"<br>"bilinear"<br>"area"<br>"bislerp" | The interpolation method used for downscaling operations |
| `upscale_method` | COMBO | No | "bicubic"<br>"nearest-exact"<br>"bilinear"<br>"area"<br>"bislerp" | The interpolation method used for upscaling operations |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with downscale patch applied |
