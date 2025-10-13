> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SVD_img2vid_Conditioning/en.md)

The SVD_img2vid_Conditioning node prepares conditioning data for video generation using Stable Video Diffusion. It takes an initial image and processes it through CLIP vision and VAE encoders to create positive and negative conditioning pairs, along with an empty latent space for video generation. This node sets up the necessary parameters for controlling motion, frame rate, and augmentation levels in the generated video.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip_vision` | CLIP_VISION | Yes | - | CLIP vision model for encoding the input image |
| `init_image` | IMAGE | Yes | - | Initial image to use as the starting point for video generation |
| `vae` | VAE | Yes | - | VAE model for encoding the image into latent space |
| `width` | INT | Yes | 16 to MAX_RESOLUTION | Output video width (default: 1024, step: 8) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | Output video height (default: 576, step: 8) |
| `video_frames` | INT | Yes | 1 to 4096 | Number of frames to generate in the video (default: 14) |
| `motion_bucket_id` | INT | Yes | 1 to 1023 | Controls the amount of motion in the generated video (default: 127) |
| `fps` | INT | Yes | 1 to 1024 | Frames per second for the generated video (default: 6) |
| `augmentation_level` | FLOAT | Yes | 0.0 to 10.0 | Level of noise augmentation to apply to the input image (default: 0.0, step: 0.01) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Positive conditioning data containing image embeddings and video parameters |
| `negative` | CONDITIONING | Negative conditioning data with zeroed embeddings and video parameters |
| `latent` | LATENT | Empty latent space tensor ready for video generation |
