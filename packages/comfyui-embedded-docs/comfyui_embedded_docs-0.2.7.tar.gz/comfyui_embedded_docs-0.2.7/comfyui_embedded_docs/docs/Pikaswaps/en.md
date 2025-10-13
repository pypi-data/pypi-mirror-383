> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Pikaswaps/en.md)

The Pika Swaps node allows you to replace objects or regions in your video with new images. You can define the areas to replace using either a mask or coordinates, and the node will seamlessly swap the specified content throughout the video sequence.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `video` | VIDEO | Yes | - | The video to swap an object in. |
| `image` | IMAGE | Yes | - | The image used to replace the masked object in the video. |
| `mask` | MASK | Yes | - | Use the mask to define areas in the video to replace. |
| `prompt_text` | STRING | Yes | - | Text prompt describing the desired replacement. |
| `negative_prompt` | STRING | Yes | - | Text prompt describing what to avoid in the replacement. |
| `seed` | INT | Yes | 0 to 4294967295 | Random seed value for consistent results. |

**Note:** This node requires all input parameters to be provided. The `video`, `image`, and `mask` work together to define the replacement operation, where the mask specifies which areas of the video will be replaced with the provided image.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The processed video with the specified object or region replaced. |
