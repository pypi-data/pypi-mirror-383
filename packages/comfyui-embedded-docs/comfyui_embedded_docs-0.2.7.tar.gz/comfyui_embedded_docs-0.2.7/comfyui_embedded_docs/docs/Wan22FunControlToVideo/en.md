> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Wan22FunControlToVideo/en.md)

The Wan22FunControlToVideo node prepares conditioning and latent representations for video generation using the Wan video model architecture. It processes positive and negative conditioning inputs along with optional reference images and control videos to create the necessary latent space representations for video synthesis. The node handles spatial scaling and temporal dimensions to generate appropriate conditioning data for video models.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning input for guiding the video generation |
| `negative` | CONDITIONING | Yes | - | Negative conditioning input for guiding the video generation |
| `vae` | VAE | Yes | - | VAE model used for encoding images to latent space |
| `width` | INT | No | 16 to MAX_RESOLUTION | Output video width in pixels (default: 832, step: 16) |
| `height` | INT | No | 16 to MAX_RESOLUTION | Output video height in pixels (default: 480, step: 16) |
| `length` | INT | No | 1 to MAX_RESOLUTION | Number of frames in the video sequence (default: 81, step: 4) |
| `batch_size` | INT | No | 1 to 4096 | Number of video sequences to generate (default: 1) |
| `ref_image` | IMAGE | No | - | Optional reference image for providing visual guidance |
| `control_video` | IMAGE | No | - | Optional control video for guiding the generation process |

**Note:** The `length` parameter is processed in chunks of 4 frames, and the node automatically handles temporal scaling for the latent space. When `ref_image` is provided, it influences the conditioning through reference latents. When `control_video` is provided, it directly affects the concat latent representation used in conditioning.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Modified positive conditioning with video-specific latent data |
| `negative` | CONDITIONING | Modified negative conditioning with video-specific latent data |
| `latent` | LATENT | Empty latent tensor with appropriate dimensions for video generation |
