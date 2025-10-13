> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanFunInpaintToVideo/en.md)

The WanFunInpaintToVideo node creates video sequences by inpainting between start and end images. It takes positive and negative conditioning along with optional frame images to generate video latents. The node handles video generation with configurable dimensions and length parameters.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning prompts for video generation |
| `negative` | CONDITIONING | Yes | - | Negative conditioning prompts to avoid in video generation |
| `vae` | VAE | Yes | - | VAE model for encoding/decoding operations |
| `width` | INT | Yes | 16 to MAX_RESOLUTION | Output video width in pixels (default: 832, step: 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | Output video height in pixels (default: 480, step: 16) |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | Number of frames in the video sequence (default: 81, step: 4) |
| `batch_size` | INT | Yes | 1 to 4096 | Number of videos to generate in a batch (default: 1) |
| `clip_vision_output` | CLIP_VISION_OUTPUT | No | - | Optional CLIP vision output for additional conditioning |
| `start_image` | IMAGE | No | - | Optional starting frame image for video generation |
| `end_image` | IMAGE | No | - | Optional ending frame image for video generation |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Processed positive conditioning output |
| `negative` | CONDITIONING | Processed negative conditioning output |
| `latent` | LATENT | Generated video latent representation |
