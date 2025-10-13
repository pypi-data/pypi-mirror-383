> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ReferenceLatent/en.md)

This node sets the guiding latent for an edit model. It takes conditioning data and an optional latent input, then modifies the conditioning to include reference latent information. If the model supports it, you can chain multiple ReferenceLatent nodes to set multiple reference images.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `conditioning` | CONDITIONING | Yes | - | The conditioning data to be modified with reference latent information |
| `latent` | LATENT | No | - | Optional latent data to use as reference for the edit model |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | CONDITIONING | The modified conditioning data containing reference latent information |
