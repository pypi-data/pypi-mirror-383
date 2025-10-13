> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/AlignYourStepsScheduler/en.md)

The AlignYourStepsScheduler node generates sigma values for the denoising process based on different model types. It calculates appropriate noise levels for each step of the sampling process and adjusts the total number of steps according to the denoise parameter. This helps align the sampling steps with the specific requirements of different diffusion models.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `model_type` | STRING | COMBO | - | SD1, SDXL, SVD | Specifies the type of model to use for sigma calculation |
| `steps` | INT | INT | 10 | 1-10000 | The total number of sampling steps to generate |
| `denoise` | FLOAT | FLOAT | 1.0 | 0.0-1.0 | Controls how much to denoise the image, where 1.0 uses all steps and lower values use fewer steps |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sigmas` | SIGMAS | Returns the calculated sigma values for the denoising process |
