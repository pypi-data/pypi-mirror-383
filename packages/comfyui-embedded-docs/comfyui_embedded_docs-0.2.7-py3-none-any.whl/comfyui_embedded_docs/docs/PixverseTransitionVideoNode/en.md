> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PixverseTransitionVideoNode/en.md)

Generates videos based on prompt and output_size. This node creates transition videos between two input images using the PixVerse API, allowing you to specify the video quality, duration, motion style, and generation parameters.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `first_frame` | IMAGE | Yes | - | The starting image for the video transition |
| `last_frame` | IMAGE | Yes | - | The ending image for the video transition |
| `prompt` | STRING | Yes | - | Prompt for the video generation (default: empty string) |
| `quality` | COMBO | Yes | Available quality options from PixverseQuality enum<br>Default: res_540p | Video quality setting |
| `duration_seconds` | COMBO | Yes | Available duration options from PixverseDuration enum | Video duration in seconds |
| `motion_mode` | COMBO | Yes | Available motion mode options from PixverseMotionMode enum | Motion style for the transition |
| `seed` | INT | Yes | 0 to 2147483647 | Seed for video generation (default: 0) |
| `negative_prompt` | STRING | No | - | An optional text description of undesired elements on an image (default: empty string) |

**Note:** When using 1080p quality, the motion mode is automatically set to normal and duration is limited to 5 seconds. For non-5 second durations, the motion mode is also automatically set to normal.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated transition video |
