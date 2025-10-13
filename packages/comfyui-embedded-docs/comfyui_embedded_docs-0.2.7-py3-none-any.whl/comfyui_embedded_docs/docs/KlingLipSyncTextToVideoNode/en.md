> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingLipSyncTextToVideoNode/en.md)

Kling Lip Sync Text to Video Node synchronizes mouth movements in a video file to match a text prompt. It takes an input video and generates a new video where the character's lip movements are aligned with the provided text. The node uses voice synthesis to create natural-looking speech synchronization.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `video` | VIDEO | Yes | - | Input video file for lip synchronization |
| `text` | STRING | Yes | - | Text Content for Lip-Sync Video Generation. Required when mode is text2video. Maximum length is 120 characters. |
| `voice` | COMBO | No | "Melody"<br>"Bella"<br>"Aria"<br>"Ethan"<br>"Ryan"<br>"Dorothy"<br>"Nathan"<br>"Lily"<br>"Aaron"<br>"Emma"<br>"Grace"<br>"Henry"<br>"Isabella"<br>"James"<br>"Katherine"<br>"Liam"<br>"Mia"<br>"Noah"<br>"Olivia"<br>"Sophia" | Voice selection for the lip-sync audio (default: "Melody") |
| `voice_speed` | FLOAT | No | 0.8-2.0 | Speech Rate. Valid range: 0.8~2.0, accurate to one decimal place. (default: 1) |

**Video Requirements:**

- Video file should not be larger than 100MB
- Height/width should be between 720px and 1920px
- Duration should be between 2s and 10s

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | Generated video with lip-synchronized audio |
| `video_id` | STRING | Unique identifier for the generated video |
| `duration` | STRING | Duration information for the generated video |
