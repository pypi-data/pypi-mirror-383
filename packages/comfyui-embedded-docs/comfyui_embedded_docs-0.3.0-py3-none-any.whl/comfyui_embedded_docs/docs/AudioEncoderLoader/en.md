> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/AudioEncoderLoader/en.md)

The AudioEncoderLoader node loads audio encoder models from your available audio encoder files. It takes an audio encoder filename as input and returns a loaded audio encoder model that can be used for audio processing tasks in your workflow.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `audio_encoder_name` | STRING | COMBO | - | Available audio encoder files | Selects which audio encoder model file to load from your audio_encoders folder |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `audio_encoder` | AUDIO_ENCODER | Returns the loaded audio encoder model for use in audio processing workflows |
