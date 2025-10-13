> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/QwenImageDiffsynthControlnet/en.md)

The QwenImageDiffsynthControlnet node applies a diffusion synthesis control network patch to modify a base model's behavior. It uses an image input and optional mask to guide the model's generation process with adjustable strength, creating a patched model that incorporates the control network's influence for more controlled image synthesis.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The base model to be patched with the control network |
| `model_patch` | MODEL_PATCH | Yes | - | The control network patch model to apply to the base model |
| `vae` | VAE | Yes | - | The VAE (Variational Autoencoder) used in the diffusion process |
| `image` | IMAGE | Yes | - | The input image used to guide the control network (only RGB channels are used) |
| `strength` | FLOAT | Yes | -10.0 to 10.0 | The strength of the control network influence (default: 1.0) |
| `mask` | MASK | No | - | Optional mask that defines areas where the control network should be applied (inverted internally) |

**Note:** When a mask is provided, it is automatically inverted (1.0 - mask) and reshaped to match the expected dimensions for the control network processing.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with the diffusion synthesis control network patch applied |
