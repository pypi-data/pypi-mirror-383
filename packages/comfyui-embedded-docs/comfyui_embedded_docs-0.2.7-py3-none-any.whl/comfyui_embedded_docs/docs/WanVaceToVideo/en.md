> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanVaceToVideo/en.md)

The WanVaceToVideo node processes video conditioning data for video generation models. It takes positive and negative conditioning inputs along with video control data and prepares latent representations for video generation. The node handles video upscaling, masking, and VAE encoding to create the appropriate conditioning structure for video models.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning input for guiding the generation |
| `negative` | CONDITIONING | Yes | - | Negative conditioning input for guiding the generation |
| `vae` | VAE | Yes | - | VAE model used for encoding images and video frames |
| `width` | INT | Yes | 16 to MAX_RESOLUTION | Output video width in pixels (default: 832, step: 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | Output video height in pixels (default: 480, step: 16) |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | Number of frames in the video (default: 81, step: 4) |
| `batch_size` | INT | Yes | 1 to 4096 | Number of videos to generate simultaneously (default: 1) |
| `strength` | FLOAT | Yes | 0.0 to 1000.0 | Control strength for video conditioning (default: 1.0, step: 0.01) |
| `control_video` | IMAGE | No | - | Optional input video for control conditioning |
| `control_masks` | MASK | No | - | Optional masks for controlling which parts of the video to modify |
| `reference_image` | IMAGE | No | - | Optional reference image for additional conditioning |

**Note:** When `control_video` is provided, it will be upscaled to match the specified width and height. If `control_masks` are provided, they must match the dimensions of the control video. The `reference_image` is encoded through the VAE and prepended to the latent sequence when provided.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Positive conditioning with video control data applied |
| `negative` | CONDITIONING | Negative conditioning with video control data applied |
| `latent` | LATENT | Empty latent tensor ready for video generation |
| `trim_latent` | INT | Number of latent frames to trim when reference image is used |
