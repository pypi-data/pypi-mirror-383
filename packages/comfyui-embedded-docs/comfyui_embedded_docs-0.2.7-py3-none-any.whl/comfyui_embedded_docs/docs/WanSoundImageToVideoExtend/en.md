> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanSoundImageToVideoExtend/en.md)

The WanSoundImageToVideoExtend node extends image-to-video generation by incorporating audio conditioning and reference images. It takes positive and negative conditioning along with video latent data and optional audio embeddings to generate extended video sequences. The node processes these inputs to create coherent video outputs that can be synchronized with audio cues.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning prompts that guide what the video should include |
| `negative` | CONDITIONING | Yes | - | Negative conditioning prompts that specify what the video should avoid |
| `vae` | VAE | Yes | - | Variational Autoencoder used for encoding and decoding video frames |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | Number of frames to generate for the video sequence (default: 77, step: 4) |
| `video_latent` | LATENT | Yes | - | Initial video latent representation that serves as the starting point for extension |
| `audio_encoder_output` | AUDIOENCODEROUTPUT | No | - | Optional audio embeddings that can influence video generation based on sound characteristics |
| `ref_image` | IMAGE | No | - | Optional reference image that provides visual guidance for the video generation |
| `control_video` | IMAGE | No | - | Optional control video that can guide the motion and style of the generated video |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Processed positive conditioning with video context applied |
| `negative` | CONDITIONING | Processed negative conditioning with video context applied |
| `latent` | LATENT | Generated video latent representation containing the extended video sequence |
