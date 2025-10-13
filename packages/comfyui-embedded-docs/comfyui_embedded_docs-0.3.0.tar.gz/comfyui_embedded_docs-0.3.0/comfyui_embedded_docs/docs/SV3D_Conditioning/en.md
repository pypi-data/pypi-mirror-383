> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SV3D_Conditioning/en.md)

The SV3D_Conditioning node prepares conditioning data for 3D video generation using the SV3D model. It takes an initial image and processes it through CLIP vision and VAE encoders to create positive and negative conditioning, along with a latent representation. The node generates camera elevation and azimuth sequences for multi-frame video generation based on the specified number of video frames.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip_vision` | CLIP_VISION | Yes | - | The CLIP vision model used for encoding the input image |
| `init_image` | IMAGE | Yes | - | The initial image that serves as the starting point for 3D video generation |
| `vae` | VAE | Yes | - | The VAE model used for encoding the image into latent space |
| `width` | INT | No | 16 to MAX_RESOLUTION | The output width for the generated video frames (default: 576, must be divisible by 8) |
| `height` | INT | No | 16 to MAX_RESOLUTION | The output height for the generated video frames (default: 576, must be divisible by 8) |
| `video_frames` | INT | No | 1 to 4096 | The number of frames to generate for the video sequence (default: 21) |
| `elevation` | FLOAT | No | -90.0 to 90.0 | The camera elevation angle in degrees for the 3D view (default: 0.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | The positive conditioning data containing image embeddings and camera parameters for generation |
| `negative` | CONDITIONING | The negative conditioning data with zeroed embeddings for contrastive generation |
| `latent` | LATENT | An empty latent tensor with dimensions matching the specified video frames and resolution |
