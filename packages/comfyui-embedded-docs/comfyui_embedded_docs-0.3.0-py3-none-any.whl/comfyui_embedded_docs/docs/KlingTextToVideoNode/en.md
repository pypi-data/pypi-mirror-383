> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingTextToVideoNode/en.md)

The Kling Text to Video Node converts text descriptions into video content. It takes text prompts and generates corresponding video sequences based on the specified configuration settings. The node supports different aspect ratios and generation modes to produce videos of varying durations and quality.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | Yes | - | Positive text prompt (default: none) |
| `negative_prompt` | STRING | Yes | - | Negative text prompt (default: none) |
| `cfg_scale` | FLOAT | No | 0.0-1.0 | Configuration scale value (default: 1.0) |
| `aspect_ratio` | COMBO | No | Options from KlingVideoGenAspectRatio | Video aspect ratio setting (default: "16:9") |
| `mode` | COMBO | No | Multiple options available | The configuration to use for the video generation following the format: mode / duration / model_name. (default: modes[4]) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video output |
| `video_id` | STRING | Unique identifier for the generated video |
| `duration` | STRING | Duration information for the generated video |
