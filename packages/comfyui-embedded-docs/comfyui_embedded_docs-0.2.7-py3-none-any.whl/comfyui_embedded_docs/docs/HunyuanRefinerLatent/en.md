> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/HunyuanRefinerLatent/en.md)

The HunyuanRefinerLatent node processes conditioning and latent inputs for refinement operations. It applies noise augmentation to both positive and negative conditioning while incorporating latent image data, and generates a new latent output with specific dimensions for further processing.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | The positive conditioning input to be processed |
| `negative` | CONDITIONING | Yes | - | The negative conditioning input to be processed |
| `latent` | LATENT | Yes | - | The latent representation input |
| `noise_augmentation` | FLOAT | Yes | 0.0 - 1.0 | The amount of noise augmentation to apply (default: 0.10) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | The processed positive conditioning with applied noise augmentation and latent image concatenation |
| `negative` | CONDITIONING | The processed negative conditioning with applied noise augmentation and latent image concatenation |
| `latent` | LATENT | A new latent output with dimensions [batch_size, 32, height, width, channels] |
