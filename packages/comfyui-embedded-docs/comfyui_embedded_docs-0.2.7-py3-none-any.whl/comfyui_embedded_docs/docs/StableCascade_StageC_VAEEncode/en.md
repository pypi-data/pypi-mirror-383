> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StableCascade_StageC_VAEEncode/en.md)

The StableCascade_StageC_VAEEncode node processes images through a VAE encoder to generate latent representations for Stable Cascade models. It takes an input image and compresses it using the specified VAE model, then outputs two latent representations: one for stage C and a placeholder for stage B. The compression parameter controls how much the image is scaled down before encoding.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The input image to be encoded into latent space |
| `vae` | VAE | Yes | - | The VAE model used for encoding the image |
| `compression` | INT | No | 4-128 | The compression factor applied to the image before encoding (default: 42) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `stage_c` | LATENT | The encoded latent representation for stage C of the Stable Cascade model |
| `stage_b` | LATENT | A placeholder latent representation for stage B (currently returns zeros) |
