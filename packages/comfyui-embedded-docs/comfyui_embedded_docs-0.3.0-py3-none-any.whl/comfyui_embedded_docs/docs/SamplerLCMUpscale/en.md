> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerLCMUpscale/en.md)

The SamplerLCMUpscale node provides a specialized sampling method that combines Latent Consistency Model (LCM) sampling with image upscaling capabilities. It allows you to upscale images during the sampling process using various interpolation methods, making it useful for generating higher resolution outputs while maintaining image quality.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `scale_ratio` | FLOAT | No | 0.1 - 20.0 | The scaling factor to apply during upscaling (default: 1.0) |
| `scale_steps` | INT | No | -1 - 1000 | The number of steps to use for upscaling process. Use -1 for automatic calculation (default: -1) |
| `upscale_method` | COMBO | Yes | "bislerp"<br>"nearest-exact"<br>"bilinear"<br>"area"<br>"bicubic" | The interpolation method used for upscaling the image |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | Returns a configured sampler object that can be used in the sampling pipeline |
