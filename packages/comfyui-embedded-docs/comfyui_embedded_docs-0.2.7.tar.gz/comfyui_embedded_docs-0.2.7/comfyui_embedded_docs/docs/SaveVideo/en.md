> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveVideo/en.md)

The SaveVideo node saves input video content to your ComfyUI output directory. It allows you to specify the filename prefix, video format, and codec for the saved file. The node automatically handles file naming with counter increments and can include workflow metadata in the saved video.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `video` | VIDEO | Yes | - | The video to save. |
| `filename_prefix` | STRING | No | - | The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd% or %Empty Latent Image.width% to include values from nodes (default: "video/ComfyUI"). |
| `format` | COMBO | No | Multiple options available | The format to save the video as (default: "auto"). |
| `codec` | COMBO | No | Multiple options available | The codec to use for the video (default: "auto"). |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| *No outputs* | - | This node does not return any output data. |
