> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SplitAudioChannels/en.md)

The SplitAudioChannels node separates stereo audio into individual left and right channels. It takes a stereo audio input with two channels and outputs two separate audio streams, one for the left channel and one for the right channel.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `audio` | AUDIO | Yes | - | The stereo audio input to be separated into channels |

**Note:** The input audio must have exactly two channels (stereo). The node will raise an error if the input audio has only one channel.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `left` | AUDIO | The separated left channel audio |
| `right` | AUDIO | The separated right channel audio |
