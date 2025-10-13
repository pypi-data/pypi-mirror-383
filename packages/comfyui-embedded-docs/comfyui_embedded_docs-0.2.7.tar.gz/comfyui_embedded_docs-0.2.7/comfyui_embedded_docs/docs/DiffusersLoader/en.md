> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/DiffusersLoader/en.md)

The DiffusersLoader node loads pre-trained models from the diffusers format. It searches for valid diffusers model directories containing a model_index.json file and loads them as MODEL, CLIP, and VAE components for use in the pipeline. This node is part of the deprecated loaders category and provides compatibility with Hugging Face diffusers models.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model_path` | STRING | Yes | Multiple options available<br>(auto-populated from diffusers folders) | The path to the diffusers model directory to load. The node automatically scans for valid diffusers models in the configured diffusers folders and lists available options. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `MODEL` | MODEL | The loaded model component from the diffusers format |
| `CLIP` | CLIP | The loaded CLIP model component from the diffusers format |
| `VAE` | VAE | The loaded VAE (Variational Autoencoder) component from the diffusers format |
