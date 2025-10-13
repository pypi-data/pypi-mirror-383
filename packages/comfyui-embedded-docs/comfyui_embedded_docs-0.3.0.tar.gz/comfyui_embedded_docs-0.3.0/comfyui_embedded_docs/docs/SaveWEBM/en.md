> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveWEBM/en.md)

The SaveWEBM node saves a sequence of images as a WEBM video file. It takes multiple input images and encodes them into a video using either VP9 or AV1 codec with configurable quality settings and frame rate. The resulting video file is saved to the output directory with metadata including prompt information.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `images` | IMAGE | Yes | - | Sequence of input images to encode as video frames |
| `filename_prefix` | STRING | No | - | Prefix for the output filename (default: "ComfyUI") |
| `codec` | COMBO | Yes | "vp9"<br>"av1" | Video codec to use for encoding |
| `fps` | FLOAT | No | 0.01-1000.0 | Frame rate for the output video (default: 24.0) |
| `crf` | FLOAT | No | 0-63.0 | Quality setting where higher crf means lower quality with smaller file size, lower crf means higher quality with larger file size (default: 32.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `ui` | PREVIEW | Video preview showing the saved WEBM file |
