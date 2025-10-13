> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ByteDanceImageReferenceNode/en.md)

The ByteDance Image Reference Node generates videos using a text prompt and one to four reference images. It sends the images and prompt to an external API service that creates a video matching your description while incorporating the visual style and content from your reference images. The node provides various controls for video resolution, aspect ratio, duration, and other generation parameters.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | COMBO | seedance_1_lite | seedance_1_lite | Model name |
| `prompt` | STRING | STRING | - | - | The text prompt used to generate the video. |
| `images` | IMAGE | IMAGE | - | - | One to four images. |
| `resolution` | STRING | COMBO | - | 480p, 720p | The resolution of the output video. |
| `aspect_ratio` | STRING | COMBO | - | adaptive, 16:9, 4:3, 1:1, 3:4, 9:16, 21:9 | The aspect ratio of the output video. |
| `duration` | INT | INT | 5 | 3-12 | The duration of the output video in seconds. |
| `seed` | INT | INT | 0 | 0-2147483647 | Seed to use for generation. |
| `watermark` | BOOLEAN | BOOLEAN | True | - | Whether to add an "AI generated" watermark to the video. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video file based on the input prompt and reference images. |
