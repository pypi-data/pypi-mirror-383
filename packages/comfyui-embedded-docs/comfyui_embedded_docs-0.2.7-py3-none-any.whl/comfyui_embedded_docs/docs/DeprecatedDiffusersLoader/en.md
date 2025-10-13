The DiffusersLoader node is designed for loading models from the diffusers library, specifically handling the loading of UNet, CLIP, and VAE models based on provided model paths. It facilitates the integration of these models into the ComfyUI framework, enabling advanced functionalities such as text-to-image generation, image manipulation, and more.

## Inputs

| Parameter    | Data Type | Description |
|--------------|--------------|-------------|
| `model_path` | COMBO[STRING] | Specifies the path to the model to be loaded. This path is crucial as it determines which model will be utilized for subsequent operations, affecting the output and capabilities of the node. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `model`   | MODEL     | The loaded UNet model, which is part of the output tuple. This model is essential for image synthesis and manipulation tasks within the ComfyUI framework. |
| `clip`    | CLIP      | The loaded CLIP model, included in the output tuple if requested. This model enables advanced text and image understanding and manipulation capabilities. |
| `vae`     | VAE       | The loaded VAE model, included in the output tuple if requested. This model is crucial for tasks involving latent space manipulation and image generation. |
