> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadVideo/en.md)

The Load Video node loads video files from the input directory and makes them available for processing in the workflow. It reads video files from the designated input folder and outputs them as video data that can be connected to other video processing nodes.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `file` | STRING | Yes | Multiple options available | The video file to load from the input directory |

**Note:** The available options for the `file` parameter are dynamically populated from the video files present in the input directory. Only video files with supported content types are displayed.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `video` | VIDEO | The loaded video data that can be passed to other video processing nodes |
