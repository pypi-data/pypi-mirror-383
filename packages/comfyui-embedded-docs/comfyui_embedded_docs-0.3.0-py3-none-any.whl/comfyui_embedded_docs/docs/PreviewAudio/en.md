> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PreviewAudio/en.md)

The PreviewAudio node generates a temporary audio preview file that can be displayed in the interface. It inherits from SaveAudio but saves files to a temporary directory with a random filename prefix. This allows users to quickly preview audio outputs without creating permanent files.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `audio` | AUDIO | Yes | - | The audio data to preview |
| `prompt` | PROMPT | No | - | Hidden parameter for internal use |
| `extra_pnginfo` | EXTRA_PNGINFO | No | - | Hidden parameter for internal use |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `ui` | UI | Displays the audio preview in the interface |
