> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/AudioMerge/en.md)

The AudioMerge node combines two audio tracks by overlaying their waveforms. It automatically matches the sample rates of both audio inputs and adjusts their lengths to be equal before merging. The node provides several mathematical methods for combining the audio signals and ensures the output remains within acceptable volume levels.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `audio1` | AUDIO | required | - | - | First audio input to merge |
| `audio2` | AUDIO | required | - | - | Second audio input to merge |
| `merge_method` | COMBO | required | - | ["add", "mean", "subtract", "multiply"] | The method used to combine the audio waveforms. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `AUDIO` | AUDIO | The merged audio output containing the combined waveform and sample rate |
