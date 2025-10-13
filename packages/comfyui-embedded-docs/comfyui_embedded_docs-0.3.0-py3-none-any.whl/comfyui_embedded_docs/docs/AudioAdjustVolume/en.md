> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/AudioAdjustVolume/en.md)

The AudioAdjustVolume node modifies the loudness of audio by applying volume adjustments in decibels. It takes an audio input and applies a gain factor based on the specified volume level, where positive values increase volume and negative values decrease it. The node returns the modified audio with the same sample rate as the original.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `audio` | AUDIO | required | - | - | The audio input to be processed |
| `volume` | INT | required | 1.0 | -100 to 100 | Volume adjustment in decibels (dB). 0 = no change, +6 = double, -6 = half, etc |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `audio` | AUDIO | The processed audio with adjusted volume level |
