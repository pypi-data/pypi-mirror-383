> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PikaImageToVideoNode2_2/en.md)

The Pika Image to Video node sends an image and text prompt to the Pika API version 2.2 to generate a video. It converts your input image into video format based on the provided description and settings. The node handles the API communication and returns the generated video as output.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The image to convert to video |
| `prompt_text` | STRING | Yes | - | The text description guiding video generation |
| `negative_prompt` | STRING | Yes | - | Text describing what to avoid in the video |
| `seed` | INT | Yes | - | Random seed value for reproducible results |
| `resolution` | STRING | Yes | - | Output video resolution setting |
| `duration` | INT | Yes | - | Length of the generated video in seconds |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video file |
