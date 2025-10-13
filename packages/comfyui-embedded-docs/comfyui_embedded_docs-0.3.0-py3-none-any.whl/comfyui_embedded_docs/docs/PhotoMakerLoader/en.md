> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PhotoMakerLoader/en.md)

The PhotoMakerLoader node loads a PhotoMaker model from the available model files. It reads the specified model file and prepares the PhotoMaker ID encoder for use in identity-based image generation tasks. This node is marked as experimental and is intended for testing purposes.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `photomaker_model_name` | STRING | Yes | Multiple options available | The name of the PhotoMaker model file to load. The available options are determined by the model files present in the photomaker folder. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `photomaker_model` | PHOTOMAKER | The loaded PhotoMaker model containing the ID encoder, ready for use in identity encoding operations. |
