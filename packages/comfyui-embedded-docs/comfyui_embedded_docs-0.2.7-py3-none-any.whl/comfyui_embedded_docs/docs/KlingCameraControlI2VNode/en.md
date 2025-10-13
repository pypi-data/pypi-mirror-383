> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingCameraControlI2VNode/en.md)

The Kling Image to Video Camera Control Node transforms still images into cinematic videos with professional camera movements. This specialized image-to-video node allows you to control virtual camera actions including zoom, rotation, pan, tilt, and first-person view while maintaining focus on your original image. Camera control is currently only supported in pro mode with the kling-v1-5 model at 5-second duration.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `start_frame` | IMAGE | Yes | - | Reference Image - URL or Base64 encoded string, cannot exceed 10MB, resolution not less than 300*300px, aspect ratio between 1:2.5 ~ 2.5:1. Base64 should not include data:image prefix. |
| `prompt` | STRING | Yes | - | Positive text prompt |
| `negative_prompt` | STRING | Yes | - | Negative text prompt |
| `cfg_scale` | FLOAT | No | 0.0-1.0 | Controls the strength of text guidance (default: 0.75) |
| `aspect_ratio` | COMBO | No | Multiple options available | Video aspect ratio selection (default: 16:9) |
| `camera_control` | CAMERA_CONTROL | Yes | - | Can be created using the Kling Camera Controls node. Controls the camera movement and motion during the video generation. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video output |
| `video_id` | STRING | Unique identifier for the generated video |
| `duration` | STRING | Duration of the generated video |
