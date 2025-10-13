> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TrimVideoLatent/en.md)

The TrimVideoLatent node removes frames from the beginning of a video latent representation. It takes a latent video sample and trims off a specified number of frames from the start, returning the remaining portion of the video. This allows you to shorten video sequences by removing the initial frames.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `samples` | LATENT | Yes | - | The input latent video representation containing the video frames to be trimmed |
| `trim_amount` | INT | No | 0 to 99999 | The number of frames to remove from the beginning of the video (default: 0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | LATENT | The trimmed latent video representation with the specified number of frames removed from the beginning |
