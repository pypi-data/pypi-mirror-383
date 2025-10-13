> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Pikadditions/en.md)

The Pikadditions node allows you to add any object or image into your video. You upload a video and specify what you'd like to add to create a seamlessly integrated result. This node uses the Pika API to insert images into videos with natural-looking integration.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `video` | VIDEO | Yes | - | The video to add an image to. |
| `image` | IMAGE | Yes | - | The image to add to the video. |
| `prompt_text` | STRING | Yes | - | Text description of what to add to the video. |
| `negative_prompt` | STRING | Yes | - | Text description of what to avoid in the video. |
| `seed` | INT | Yes | 0 to 4294967295 | Random seed value for reproducible results. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The processed video with the image inserted. |
