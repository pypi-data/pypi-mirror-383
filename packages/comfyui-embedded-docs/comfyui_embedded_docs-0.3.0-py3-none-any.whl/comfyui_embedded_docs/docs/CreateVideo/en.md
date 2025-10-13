> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CreateVideo/en.md)

The Create Video node generates a video file from a sequence of images. You can specify the playback speed using frames per second and optionally add audio to the video. The node combines your images into a video format that can be played back with the specified frame rate.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `images` | IMAGE | Yes | - | The images to create a video from. |
| `fps` | FLOAT | Yes | 1.0 - 120.0 | The frames per second for the video playback speed (default: 30.0). |
| `audio` | AUDIO | No | - | The audio to add to the video. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video file containing the input images and optional audio. |
