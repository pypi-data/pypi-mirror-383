> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanHuMoImageToVideo/en.md)

The WanHuMoImageToVideo node converts images to video sequences by generating latent representations for video frames. It processes conditioning inputs and can incorporate reference images and audio embeddings to influence the video generation. The node outputs modified conditioning data and latent representations suitable for video synthesis.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning input that guides the video generation toward desired content |
| `negative` | CONDITIONING | Yes | - | Negative conditioning input that steers the video generation away from unwanted content |
| `vae` | VAE | Yes | - | VAE model used for encoding reference images into latent space |
| `width` | INT | Yes | 16 to MAX_RESOLUTION | Width of the output video frames in pixels (default: 832, must be divisible by 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | Height of the output video frames in pixels (default: 480, must be divisible by 16) |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | Number of frames in the generated video sequence (default: 97) |
| `batch_size` | INT | Yes | 1 to 4096 | Number of video sequences to generate simultaneously (default: 1) |
| `audio_encoder_output` | AUDIOENCODEROUTPUT | No | - | Optional audio encoding data that can influence video generation based on audio content |
| `ref_image` | IMAGE | No | - | Optional reference image used to guide the video generation style and content |

**Note:** When a reference image is provided, it gets encoded and added to both positive and negative conditioning. When audio encoder output is provided, it gets processed and incorporated into the conditioning data.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Modified positive conditioning with reference image and/or audio embeddings incorporated |
| `negative` | CONDITIONING | Modified negative conditioning with reference image and/or audio embeddings incorporated |
| `latent` | LATENT | Generated latent representation containing the video sequence data |
