> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ImageOnlyCheckpointSave/en.md)

The ImageOnlyCheckpointSave node saves a checkpoint file containing a model, CLIP vision encoder, and VAE. It creates a safetensors file with the specified filename prefix and stores it in the output directory. This node is specifically designed for saving image-related model components together in a single checkpoint file.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to be saved in the checkpoint |
| `clip_vision` | CLIP_VISION | Yes | - | The CLIP vision encoder to be saved in the checkpoint |
| `vae` | VAE | Yes | - | The VAE (Variational Autoencoder) to be saved in the checkpoint |
| `filename_prefix` | STRING | Yes | - | The prefix for the output filename (default: "checkpoints/ComfyUI") |
| `prompt` | PROMPT | No | - | Hidden parameter for workflow prompt data |
| `extra_pnginfo` | EXTRA_PNGINFO | No | - | Hidden parameter for additional PNG metadata |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| - | - | This node does not return any outputs |
