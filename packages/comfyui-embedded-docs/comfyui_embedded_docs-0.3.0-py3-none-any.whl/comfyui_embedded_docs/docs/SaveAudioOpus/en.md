> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveAudioOpus/en.md)

The SaveAudioOpus node saves audio data to an Opus format file. It takes audio input and exports it as a compressed Opus file with configurable quality settings. The node automatically handles file naming and saves the output to the designated output directory.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `audio` | AUDIO | Yes | - | The audio data to be saved as an Opus file |
| `filename_prefix` | STRING | No | - | The prefix for the output filename (default: "audio/ComfyUI") |
| `quality` | COMBO | No | "64k"<br>"96k"<br>"128k"<br>"192k"<br>"320k" | The audio quality setting for the Opus file (default: "128k") |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| - | - | This node does not return any output values. It saves the audio file to disk as its primary function. |
