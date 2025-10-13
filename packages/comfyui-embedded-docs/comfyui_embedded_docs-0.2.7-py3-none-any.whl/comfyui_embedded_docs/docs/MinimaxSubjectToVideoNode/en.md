> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/MinimaxSubjectToVideoNode/en.md)

Generates videos synchronously based on an image and prompt, and optional parameters using MiniMax's API. This node takes a subject image and text description to create a video using MiniMax's video generation service.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `subject` | IMAGE | Yes | - | Image of subject to reference for video generation |
| `prompt_text` | STRING | Yes | - | Text prompt to guide the video generation (default: empty string) |
| `model` | COMBO | No | "S2V-01"<br> | Model to use for video generation (default: "S2V-01") |
| `seed` | INT | No | 0 to 18446744073709551615 | The random seed used for creating the noise (default: 0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video based on the input subject image and prompt |
