> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PikaTextToVideoNode2_2/en.md)

The Pika Text2Video v2.2 Node sends a text prompt to the Pika API version 2.2 to generate a video. It converts your text description into a video using Pika's AI video generation service. The node allows you to customize various aspects of the video generation process including aspect ratio, duration, and resolution.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `prompt_text` | STRING | Yes | - | The main text description that describes what you want to generate in the video |
| `negative_prompt` | STRING | Yes | - | Text describing what you don't want to appear in the generated video |
| `seed` | INT | Yes | - | A number that controls the randomness of the generation for reproducible results |
| `resolution` | STRING | Yes | - | The resolution setting for the output video |
| `duration` | INT | Yes | - | The length of the video in seconds |
| `aspect_ratio` | FLOAT | No | 0.4 - 2.5 | Aspect ratio (width / height) (default: 1.7777777777777777) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video file returned from the Pika API |
