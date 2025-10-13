> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentBlend/en.md)

The LatentBlend node combines two latent samples by blending them together using a specified blend factor. It takes two latent inputs and creates a new output where the first sample is weighted by the blend factor and the second sample is weighted by the inverse. If the input samples have different shapes, the second sample is automatically resized to match the first sample's dimensions.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `samples1` | LATENT | Yes | - | The first latent sample to blend |
| `samples2` | LATENT | Yes | - | The second latent sample to blend |
| `blend_factor` | FLOAT | Yes | 0 to 1 | Controls the blending ratio between the two samples (default: 0.5) |

**Note:** If `samples1` and `samples2` have different shapes, `samples2` will be automatically resized to match the dimensions of `samples1` using bicubic interpolation with center cropping.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `latent` | LATENT | The blended latent sample combining both input samples |
