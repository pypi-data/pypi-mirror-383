> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanCameraImageToVideo/en.md)

The WanCameraImageToVideo node converts images to video sequences by generating latent representations for video generation. It processes conditioning inputs and optional starting images to create video latents that can be used with video models. The node supports camera conditions and clip vision outputs for enhanced video generation control.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning prompts for video generation |
| `negative` | CONDITIONING | Yes | - | Negative conditioning prompts to avoid in video generation |
| `vae` | VAE | Yes | - | VAE model for encoding images to latent space |
| `width` | INT | Yes | 16 to MAX_RESOLUTION | Output video width in pixels (default: 832, step: 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | Output video height in pixels (default: 480, step: 16) |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | Number of frames in the video sequence (default: 81, step: 4) |
| `batch_size` | INT | Yes | 1 to 4096 | Number of videos to generate simultaneously (default: 1) |
| `clip_vision_output` | CLIP_VISION_OUTPUT | No | - | Optional CLIP vision output for additional conditioning |
| `start_image` | IMAGE | No | - | Optional starting image to initialize the video sequence |
| `camera_conditions` | WAN_CAMERA_EMBEDDING | No | - | Optional camera embedding conditions for video generation |

**Note:** When `start_image` is provided, the node uses it to initialize the video sequence and applies masking to blend the starting frames with generated content. The `camera_conditions` and `clip_vision_output` parameters are optional but when provided, they modify the conditioning for both positive and negative prompts.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Modified positive conditioning with applied camera conditions and clip vision outputs |
| `negative` | CONDITIONING | Modified negative conditioning with applied camera conditions and clip vision outputs |
| `latent` | LATENT | Generated video latent representation for use with video models |
