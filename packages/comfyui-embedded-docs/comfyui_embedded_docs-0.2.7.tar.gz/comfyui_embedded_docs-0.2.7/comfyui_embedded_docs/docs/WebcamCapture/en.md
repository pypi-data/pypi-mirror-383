> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WebcamCapture/en.md)

The WebcamCapture node captures images from a webcam device and converts them into a format that can be used within ComfyUI workflows. It inherits from the LoadImage node and provides options to control the capture dimensions and timing. When enabled, the node can capture new images each time the workflow queue is processed.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | WEBCAM | Yes | - | The webcam input source to capture images from |
| `width` | INT | No | 0 to MAX_RESOLUTION | The desired width for the captured image (default: 0, uses webcam's native resolution) |
| `height` | INT | No | 0 to MAX_RESOLUTION | The desired height for the captured image (default: 0, uses webcam's native resolution) |
| `capture_on_queue` | BOOLEAN | No | - | When enabled, captures a new image each time the workflow queue is processed (default: True) |

**Note:** When both `width` and `height` are set to 0, the node uses the webcam's native resolution. Setting either dimension to a non-zero value will resize the captured image accordingly.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | The captured webcam image converted to ComfyUI's image format |
