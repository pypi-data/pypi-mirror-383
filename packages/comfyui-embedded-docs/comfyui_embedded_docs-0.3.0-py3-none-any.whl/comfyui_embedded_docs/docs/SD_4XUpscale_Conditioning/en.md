> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SD_4XUpscale_Conditioning/en.md)

The SD_4XUpscale_Conditioning node prepares conditioning data for upscaling images using diffusion models. It takes input images and conditioning data, then applies scaling and noise augmentation to create modified conditioning that guides the upscaling process. The node outputs both positive and negative conditioning along with latent representations for the upscaled dimensions.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `images` | IMAGE | Yes | - | Input images to be upscaled |
| `positive` | CONDITIONING | Yes | - | Positive conditioning data that guides the generation toward desired content |
| `negative` | CONDITIONING | Yes | - | Negative conditioning data that steers the generation away from unwanted content |
| `scale_ratio` | FLOAT | No | 0.0 - 10.0 | Scaling factor applied to the input images (default: 4.0) |
| `noise_augmentation` | FLOAT | No | 0.0 - 1.0 | Amount of noise to add during the upscaling process (default: 0.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Modified positive conditioning with upscaling information applied |
| `negative` | CONDITIONING | Modified negative conditioning with upscaling information applied |
| `latent` | LATENT | Empty latent representation matching the upscaled dimensions |
