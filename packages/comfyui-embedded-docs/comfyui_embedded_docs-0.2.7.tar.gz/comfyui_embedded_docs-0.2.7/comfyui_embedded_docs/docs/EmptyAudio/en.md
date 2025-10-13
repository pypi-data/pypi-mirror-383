> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/EmptyAudio/en.md)

The EmptyAudio node generates a silent audio clip with specified duration, sample rate, and channel configuration. It creates a waveform containing all zeros, producing complete silence for the given duration. This node is useful for creating placeholder audio or generating silent segments in audio workflows.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `duration` | FLOAT | Yes | 0.0 to 1.8446744073709552e+19 | Duration of the empty audio clip in seconds (default: 60.0) |
| `sample_rate` | INT | Yes | - | Sample rate of the empty audio clip (default: 44100) |
| `channels` | INT | Yes | 1 to 2 | Number of audio channels (1 for mono, 2 for stereo) (default: 2) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `AUDIO` | AUDIO | The generated silent audio clip containing waveform data and sample rate information |
