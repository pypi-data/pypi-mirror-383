> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingCameraControlT2VNode/en.md)

Kling Text to Video Camera Control Node transforms text into cinematic videos with professional camera movements that simulate real-world cinematography. This node supports controlling virtual camera actions including zoom, rotation, pan, tilt, and first-person view while maintaining focus on your original text. The duration, mode, and model name are hard-coded because camera control is only supported in pro mode with the kling-v1-5 model at 5-second duration.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | Yes | - | Positive text prompt |
| `negative_prompt` | STRING | Yes | - | Negative text prompt |
| `cfg_scale` | FLOAT | No | 0.0-1.0 | Controls how closely the output follows the prompt (default: 0.75) |
| `aspect_ratio` | COMBO | No | "16:9"<br>"9:16"<br>"1:1"<br>"21:9"<br>"3:4"<br>"4:3" | The aspect ratio for the generated video (default: "16:9") |
| `camera_control` | CAMERA_CONTROL | No | - | Can be created using the Kling Camera Controls node. Controls the camera movement and motion during the video generation. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video with camera control effects |
| `video_id` | STRING | The unique identifier for the generated video |
| `duration` | STRING | The duration of the generated video |
