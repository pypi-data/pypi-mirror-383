> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveLatent/en.md)

The SaveLatent node saves latent tensors to disk as files for later use or sharing. It takes latent samples and saves them to the output directory with optional metadata including prompt information. The node automatically handles file naming and organization while preserving the latent data structure.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `samples` | LATENT | Yes | - | The latent samples to be saved to disk |
| `filename_prefix` | STRING | No | - | The prefix for the output filename (default: "latents/ComfyUI") |
| `prompt` | PROMPT | No | - | Prompt information to include in metadata (hidden parameter) |
| `extra_pnginfo` | EXTRA_PNGINFO | No | - | Additional PNG information to include in metadata (hidden parameter) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `ui` | UI | Provides file location information for the saved latent in the ComfyUI interface |
