> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadLatent/en.md)

The LoadLatent node loads previously saved latent representations from .latent files in the input directory. It reads the latent tensor data from the file and applies any necessary scaling adjustments before returning the latent data for use in other nodes.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `latent` | STRING | Yes | All .latent files in input directory | Selects which .latent file to load from the available files in the input directory |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `LATENT` | LATENT | Returns the loaded latent representation data from the selected file |
