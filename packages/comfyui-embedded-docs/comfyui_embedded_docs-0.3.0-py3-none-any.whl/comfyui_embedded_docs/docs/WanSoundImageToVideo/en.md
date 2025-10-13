> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanSoundImageToVideo/en.md)

The WanSoundImageToVideo node generates video content from images with optional audio conditioning. It takes positive and negative conditioning prompts along with a VAE model to create video latents, and can incorporate reference images, audio encoding, control videos, and motion references to guide the video generation process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning prompts that guide what content should appear in the generated video |
| `negative` | CONDITIONING | Yes | - | Negative conditioning prompts that specify what content should be avoided in the generated video |
| `vae` | VAE | Yes | - | VAE model used for encoding and decoding the video latent representations |
| `width` | INT | Yes | 16 to MAX_RESOLUTION | Width of the output video in pixels (default: 832, must be divisible by 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | Height of the output video in pixels (default: 480, must be divisible by 16) |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | Number of frames in the generated video (default: 77, must be divisible by 4) |
| `batch_size` | INT | Yes | 1 to 4096 | Number of videos to generate simultaneously (default: 1) |
| `audio_encoder_output` | AUDIOENCODEROUTPUT | No | - | Optional audio encoding that can influence the video generation based on sound characteristics |
| `ref_image` | IMAGE | No | - | Optional reference image that provides visual guidance for the video content |
| `control_video` | IMAGE | No | - | Optional control video that guides the motion and structure of the generated video |
| `ref_motion` | IMAGE | No | - | Optional motion reference that provides guidance for movement patterns in the video |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Processed positive conditioning that has been modified for video generation |
| `negative` | CONDITIONING | Processed negative conditioning that has been modified for video generation |
| `latent` | LATENT | Generated video representation in latent space that can be decoded into final video frames |
