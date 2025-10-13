> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/OptimalStepsScheduler/en.md)

The OptimalStepsScheduler node calculates noise schedule sigmas for diffusion models based on the selected model type and step configuration. It adjusts the total number of steps according to the denoise parameter and interpolates the noise levels to match the requested step count. The node returns a sequence of sigma values that determine the noise levels used during the diffusion sampling process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model_type` | COMBO | Yes | "FLUX"<br>"Wan"<br>"Chroma" | The type of diffusion model to use for noise level calculation |
| `steps` | INT | Yes | 3-1000 | The total number of sampling steps to calculate (default: 20) |
| `denoise` | FLOAT | No | 0.0-1.0 | Controls the denoising strength, which adjusts the effective number of steps (default: 1.0) |

**Note:** When `denoise` is set to less than 1.0, the node calculates the effective steps as `steps * denoise`. If `denoise` is set to 0.0, the node returns an empty tensor.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sigmas` | SIGMAS | A sequence of sigma values representing the noise schedule for diffusion sampling |
