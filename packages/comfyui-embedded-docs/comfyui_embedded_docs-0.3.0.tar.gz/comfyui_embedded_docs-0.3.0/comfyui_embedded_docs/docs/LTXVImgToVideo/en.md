> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LTXVImgToVideo/en.md)

The LTXVImgToVideo node converts an input image into a video latent representation for video generation models. It takes a single image and extends it into a sequence of frames using the VAE encoder, then applies conditioning with strength control to determine how much of the original image content is preserved versus modified during video generation.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning prompts for guiding the video generation |
| `negative` | CONDITIONING | Yes | - | Negative conditioning prompts for avoiding certain elements in the video |
| `vae` | VAE | Yes | - | VAE model used for encoding the input image into latent space |
| `image` | IMAGE | Yes | - | Input image to be converted into video frames |
| `width` | INT | No | 64 to MAX_RESOLUTION | Output video width in pixels (default: 768, step: 32) |
| `height` | INT | No | 64 to MAX_RESOLUTION | Output video height in pixels (default: 512, step: 32) |
| `length` | INT | No | 9 to MAX_RESOLUTION | Number of frames in the generated video (default: 97, step: 8) |
| `batch_size` | INT | No | 1 to 4096 | Number of videos to generate simultaneously (default: 1) |
| `strength` | FLOAT | No | 0.0 to 1.0 | Control over how much the original image is modified during video generation, where 1.0 preserves most of the original content and 0.0 allows maximum modification (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Processed positive conditioning with video frame masking applied |
| `negative` | CONDITIONING | Processed negative conditioning with video frame masking applied |
| `latent` | LATENT | Video latent representation containing the encoded frames and noise mask for video generation |
