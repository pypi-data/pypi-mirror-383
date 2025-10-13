> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanAnimateToVideo/en.md)

The WanAnimateToVideo node generates video content by combining multiple conditioning inputs including pose references, facial expressions, and background elements. It processes various video inputs to create coherent animated sequences while maintaining temporal consistency across frames. The node handles latent space operations and can extend existing videos by continuing motion patterns.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning for guiding the generation towards desired content |
| `negative` | CONDITIONING | Yes | - | Negative conditioning for steering the generation away from unwanted content |
| `vae` | VAE | Yes | - | VAE model used for encoding and decoding image data |
| `width` | INT | No | 16 to MAX_RESOLUTION | Output video width in pixels (default: 832, step: 16) |
| `height` | INT | No | 16 to MAX_RESOLUTION | Output video height in pixels (default: 480, step: 16) |
| `length` | INT | No | 1 to MAX_RESOLUTION | Number of frames to generate (default: 77, step: 4) |
| `batch_size` | INT | No | 1 to 4096 | Number of videos to generate simultaneously (default: 1) |
| `clip_vision_output` | CLIP_VISION_OUTPUT | No | - | Optional CLIP vision model output for additional conditioning |
| `reference_image` | IMAGE | No | - | Reference image used as starting point for generation |
| `face_video` | IMAGE | No | - | Video input providing facial expression guidance |
| `pose_video` | IMAGE | No | - | Video input providing pose and motion guidance |
| `continue_motion_max_frames` | INT | No | 1 to MAX_RESOLUTION | Maximum number of frames to continue from previous motion (default: 5, step: 4) |
| `background_video` | IMAGE | No | - | Background video to composite with generated content |
| `character_mask` | MASK | No | - | Mask defining character regions for selective processing |
| `continue_motion` | IMAGE | No | - | Previous motion sequence to continue from for temporal consistency |
| `video_frame_offset` | INT | No | 0 to MAX_RESOLUTION | The amount of frames to seek in all the input videos. Used for generating longer videos by chunk. Connect to the video_frame_offset output of the previous node for extending a video. (default: 0, step: 1) |

**Parameter Constraints:**

- When `pose_video` is provided and `trim_to_pose_video` logic is active, the output length will be adjusted to match the pose video duration
- `face_video` is automatically resized to 512x512 resolution when processed
- `continue_motion` frames are limited by `continue_motion_max_frames` parameter
- Input videos (`face_video`, `pose_video`, `background_video`, `character_mask`) are offset by `video_frame_offset` before processing
- If `character_mask` contains only one frame, it will be repeated across all frames
- When `clip_vision_output` is provided, it's applied to both positive and negative conditioning

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Modified positive conditioning with additional video context |
| `negative` | CONDITIONING | Modified negative conditioning with additional video context |
| `latent` | LATENT | Generated video content in latent space format |
| `trim_latent` | INT | Latent space trimming information for downstream processing |
| `trim_image` | INT | Image space trimming information for reference motion frames |
| `video_frame_offset` | INT | Updated frame offset for continuing video generation in chunks |
