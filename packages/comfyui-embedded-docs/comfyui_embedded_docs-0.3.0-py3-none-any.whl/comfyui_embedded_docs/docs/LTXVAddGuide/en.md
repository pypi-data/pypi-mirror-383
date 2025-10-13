> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LTXVAddGuide/en.md)

The LTXVAddGuide node adds video conditioning guidance to latent sequences by encoding input images or videos and incorporating them as keyframes into the conditioning data. It processes the input through a VAE encoder and strategically places the resulting latents at specified frame positions while updating both positive and negative conditioning with keyframe information. The node handles frame alignment constraints and allows control over the strength of the conditioning influence.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning input to be modified with keyframe guidance |
| `negative` | CONDITIONING | Yes | - | Negative conditioning input to be modified with keyframe guidance |
| `vae` | VAE | Yes | - | VAE model used for encoding the input image/video frames |
| `latent` | LATENT | Yes | - | Input latent sequence that will receive the conditioning frames |
| `image` | IMAGE | Yes | - | Image or video to condition the latent video on. Must be 8*n + 1 frames. If the video is not 8*n + 1 frames, it will be cropped to the nearest 8*n + 1 frames. |
| `frame_idx` | INT | No | -9999 to 9999 | Frame index to start the conditioning at. For single-frame images or videos with 1-8 frames, any frame_idx value is acceptable. For videos with 9+ frames, frame_idx must be divisible by 8, otherwise it will be rounded down to the nearest multiple of 8. Negative values are counted from the end of the video. (default: 0) |
| `strength` | FLOAT | No | 0.0 to 1.0 | Strength of the conditioning influence, where 1.0 applies full conditioning and 0.0 applies no conditioning (default: 1.0) |

**Note:** The input image/video must have a frame count following the 8*n + 1 pattern (e.g., 1, 9, 17, 25 frames). If the input exceeds this pattern, it will be automatically cropped to the nearest valid frame count.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Positive conditioning updated with keyframe guidance information |
| `negative` | CONDITIONING | Negative conditioning updated with keyframe guidance information |
| `latent` | LATENT | Latent sequence with incorporated conditioning frames and updated noise mask |
