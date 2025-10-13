> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PikaStartEndFrameNode2_2/en.md)

The PikaFrames v2.2 Node generates videos by combining your first and last frame. You upload two images to define the start and end points, and the AI creates a smooth transition between them to produce a complete video.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image_start` | IMAGE | Yes | - | The first image to combine. |
| `image_end` | IMAGE | Yes | - | The last image to combine. |
| `prompt_text` | STRING | Yes | - | Text prompt describing the desired video content. |
| `negative_prompt` | STRING | Yes | - | Text describing what to avoid in the video. |
| `seed` | INT | Yes | - | Random seed value for generation consistency. |
| `resolution` | STRING | Yes | - | Output video resolution. |
| `duration` | INT | Yes | - | Duration of the generated video. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video combining the start and end frames with AI transitions. |
