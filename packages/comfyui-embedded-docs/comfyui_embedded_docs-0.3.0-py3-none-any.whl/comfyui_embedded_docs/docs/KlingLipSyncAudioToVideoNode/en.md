> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingLipSyncAudioToVideoNode/en.md)

Kling Lip Sync Audio to Video Node synchronizes mouth movements in a video file to match the audio content of an audio file. This node analyzes the vocal patterns in the audio and adjusts the facial movements in the video to create realistic lip-syncing. The process requires both a video containing a distinct face and an audio file with clearly distinguishable vocals.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `video` | VIDEO | Yes | - | The video file containing a face to be lip-synced |
| `audio` | AUDIO | Yes | - | The audio file containing vocals to sync with the video |
| `voice_language` | COMBO | No | `"en"`<br>`"zh"`<br>`"es"`<br>`"fr"`<br>`"de"`<br>`"it"`<br>`"pt"`<br>`"pl"`<br>`"tr"`<br>`"ru"`<br>`"nl"`<br>`"cs"`<br>`"ar"`<br>`"ja"`<br>`"hu"`<br>`"ko"` | The language of the voice in the audio file (default: "en") |

**Important Constraints:**

- The audio file should not be larger than 5MB
- The video file should not be larger than 100MB
- Video dimensions should be between 720px and 1920px in height/width
- Video duration should be between 2 seconds and 10 seconds
- The audio must contain clearly distinguishable vocals
- The video must contain a distinct face

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The processed video with lip-synced mouth movements |
| `video_id` | STRING | The unique identifier for the processed video |
| `duration` | STRING | The duration of the processed video |
