> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TrimAudioDuration/en.md)

The TrimAudioDuration node allows you to cut a specific time segment from an audio file. You can specify when to start the trim and how long the resulting audio clip should be. The node works by converting time values to audio frame positions and extracting the corresponding portion of the audio waveform.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `audio` | AUDIO | Yes | - | The audio input to be trimmed |
| `start_index` | FLOAT | Yes | -0xffffffffffffffff to 0xffffffffffffffff | Start time in seconds, can be negative to count from the end (supports sub-seconds). Default: 0.0 |
| `duration` | FLOAT | Yes | 0.0 to 0xffffffffffffffff | Duration in seconds. Default: 60.0 |

**Note:** The start time must be less than the end time and within the audio length. Negative start values count backwards from the end of the audio.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `audio` | AUDIO | The trimmed audio segment with the specified start time and duration |
