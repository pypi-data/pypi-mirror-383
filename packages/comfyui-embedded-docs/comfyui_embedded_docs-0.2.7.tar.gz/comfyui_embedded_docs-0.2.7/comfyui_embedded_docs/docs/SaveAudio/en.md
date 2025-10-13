> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveAudio/en.md)

The SaveAudio node saves audio data to a file in FLAC format. It takes audio input and writes it to the specified output directory with the given filename prefix. The node automatically handles file naming and ensures the audio is properly saved for later use.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `audio` | AUDIO | Yes | - | The audio data to be saved |
| `filename_prefix` | STRING | No | - | The prefix for the output filename (default: "audio/ComfyUI") |

*Note: The `prompt` and `extra_pnginfo` parameters are hidden and automatically handled by the system.*

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| *None* | - | This node does not return any output data but saves the audio file to the output directory |
