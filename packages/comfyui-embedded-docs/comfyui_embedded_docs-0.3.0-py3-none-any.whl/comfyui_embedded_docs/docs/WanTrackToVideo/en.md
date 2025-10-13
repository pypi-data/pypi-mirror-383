> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanTrackToVideo/en.md)

The WanTrackToVideo node converts motion tracking data into video sequences by processing track points and generating corresponding video frames. It takes tracking coordinates as input and produces video conditioning and latent representations that can be used for video generation. When no tracks are provided, it falls back to standard image-to-video conversion.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning for video generation |
| `negative` | CONDITIONING | Yes | - | Negative conditioning for video generation |
| `vae` | VAE | Yes | - | VAE model for encoding and decoding |
| `tracks` | STRING | Yes | - | JSON-formatted tracking data as a multiline string (default: "[]") |
| `width` | INT | Yes | 16 to MAX_RESOLUTION | Output video width in pixels (default: 832, step: 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | Output video height in pixels (default: 480, step: 16) |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | Number of frames in the output video (default: 81, step: 4) |
| `batch_size` | INT | Yes | 1 to 4096 | Number of videos to generate simultaneously (default: 1) |
| `temperature` | FLOAT | Yes | 1.0 to 1000.0 | Temperature parameter for motion patching (default: 220.0, step: 0.1) |
| `topk` | INT | Yes | 1 to 10 | Top-k value for motion patching (default: 2) |
| `start_image` | IMAGE | No | - | Starting image for video generation |
| `clip_vision_output` | CLIPVISIONOUTPUT | No | - | CLIP vision output for additional conditioning |

**Note:** When `tracks` contains valid tracking data, the node processes motion tracks to generate video. When `tracks` is empty, it switches to standard image-to-video mode. If `start_image` is provided, it initializes the first frame of the video sequence.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Positive conditioning with motion track information applied |
| `negative` | CONDITIONING | Negative conditioning with motion track information applied |
| `latent` | LATENT | Generated video latent representation |
