> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanImageToVideo/en.md)

The WanImageToVideo node prepares conditioning and latent representations for video generation tasks. It creates an empty latent space for video generation and can optionally incorporate starting images and CLIP vision outputs to guide the video generation process. The node modifies both positive and negative conditioning inputs based on the provided image and vision data.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning input for guiding the generation |
| `negative` | CONDITIONING | Yes | - | Negative conditioning input for guiding the generation |
| `vae` | VAE | Yes | - | VAE model for encoding images to latent space |
| `width` | INT | Yes | 16 to MAX_RESOLUTION | Width of the output video (default: 832, step: 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | Height of the output video (default: 480, step: 16) |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | Number of frames in the video (default: 81, step: 4) |
| `batch_size` | INT | Yes | 1 to 4096 | Number of videos to generate in a batch (default: 1) |
| `clip_vision_output` | CLIP_VISION_OUTPUT | No | - | Optional CLIP vision output for additional conditioning |
| `start_image` | IMAGE | No | - | Optional starting image to initialize the video generation |

**Note:** When `start_image` is provided, the node encodes the image sequence and applies masking to the conditioning inputs. The `clip_vision_output` parameter, when provided, adds vision-based conditioning to both positive and negative inputs.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Modified positive conditioning with image and vision data incorporated |
| `negative` | CONDITIONING | Modified negative conditioning with image and vision data incorporated |
| `latent` | LATENT | Empty latent space tensor ready for video generation |
