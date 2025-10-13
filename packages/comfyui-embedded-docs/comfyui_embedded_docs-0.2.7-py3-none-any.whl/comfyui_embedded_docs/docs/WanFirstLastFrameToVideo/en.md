> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanFirstLastFrameToVideo/en.md)

The WanFirstLastFrameToVideo node creates video conditioning by combining start and end frames with text prompts. It generates a latent representation for video generation by encoding the first and last frames, applying masks to guide the generation process, and incorporating CLIP vision features when available. This node prepares both positive and negative conditioning for video models to generate coherent sequences between specified start and end points.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive text conditioning for guiding the video generation |
| `negative` | CONDITIONING | Yes | - | Negative text conditioning for guiding the video generation |
| `vae` | VAE | Yes | - | VAE model used for encoding images to latent space |
| `width` | INT | No | 16 to MAX_RESOLUTION | Output video width (default: 832, step: 16) |
| `height` | INT | No | 16 to MAX_RESOLUTION | Output video height (default: 480, step: 16) |
| `length` | INT | No | 1 to MAX_RESOLUTION | Number of frames in the video sequence (default: 81, step: 4) |
| `batch_size` | INT | No | 1 to 4096 | Number of videos to generate simultaneously (default: 1) |
| `clip_vision_start_image` | CLIP_VISION_OUTPUT | No | - | CLIP vision features extracted from the start image |
| `clip_vision_end_image` | CLIP_VISION_OUTPUT | No | - | CLIP vision features extracted from the end image |
| `start_image` | IMAGE | No | - | Starting frame image for the video sequence |
| `end_image` | IMAGE | No | - | Ending frame image for the video sequence |

**Note:** When both `start_image` and `end_image` are provided, the node creates a video sequence that transitions between these two frames. The `clip_vision_start_image` and `clip_vision_end_image` parameters are optional but when provided, their CLIP vision features are concatenated and applied to both positive and negative conditioning.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Positive conditioning with applied video frame encoding and CLIP vision features |
| `negative` | CONDITIONING | Negative conditioning with applied video frame encoding and CLIP vision features |
| `latent` | LATENT | Empty latent tensor with dimensions matching the specified video parameters |
