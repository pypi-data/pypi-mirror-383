> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanPhantomSubjectToVideo/en.md)

The WanPhantomSubjectToVideo node generates video content by processing conditioning inputs and optional reference images. It creates latent representations for video generation and can incorporate visual guidance from input images when provided. The node prepares conditioning data with time-dimensional concatenation for video models and outputs modified conditioning along with generated latent video data.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning input for guiding video generation |
| `negative` | CONDITIONING | Yes | - | Negative conditioning input to avoid certain characteristics |
| `vae` | VAE | Yes | - | VAE model for encoding images when provided |
| `width` | INT | No | 16 to MAX_RESOLUTION | Output video width in pixels (default: 832, must be divisible by 16) |
| `height` | INT | No | 16 to MAX_RESOLUTION | Output video height in pixels (default: 480, must be divisible by 16) |
| `length` | INT | No | 1 to MAX_RESOLUTION | Number of frames in the generated video (default: 81, must be divisible by 4) |
| `batch_size` | INT | No | 1 to 4096 | Number of videos to generate simultaneously (default: 1) |
| `images` | IMAGE | No | - | Optional reference images for time-dimensional conditioning |

**Note:** When `images` are provided, they are automatically upscaled to match the specified `width` and `height`, and only the first `length` frames are used for processing.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Modified positive conditioning with time-dimensional concatenation when images are provided |
| `negative_text` | CONDITIONING | Modified negative conditioning with time-dimensional concatenation when images are provided |
| `negative_img_text` | CONDITIONING | Negative conditioning with zeroed time-dimensional concatenation when images are provided |
| `latent` | LATENT | Generated latent video representation with specified dimensions and length |
