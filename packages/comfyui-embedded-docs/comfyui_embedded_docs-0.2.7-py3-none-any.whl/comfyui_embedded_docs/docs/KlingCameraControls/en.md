> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingCameraControls/en.md)

The Kling Camera Controls node allows you to configure various camera movement and rotation parameters for creating motion control effects in video generation. It provides controls for camera positioning, rotation, and zoom to simulate different camera movements.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `camera_control_type` | COMBO | Yes | Multiple options available | Specifies the type of camera control configuration to use |
| `horizontal_movement` | FLOAT | No | -10.0 to 10.0 | Controls camera's movement along horizontal axis (x-axis). Negative indicates left, positive indicates right (default: 0.0) |
| `vertical_movement` | FLOAT | No | -10.0 to 10.0 | Controls camera's movement along vertical axis (y-axis). Negative indicates downward, positive indicates upward (default: 0.0) |
| `pan` | FLOAT | No | -10.0 to 10.0 | Controls camera's rotation in vertical plane (x-axis). Negative indicates downward rotation, positive indicates upward rotation (default: 0.5) |
| `tilt` | FLOAT | No | -10.0 to 10.0 | Controls camera's rotation in horizontal plane (y-axis). Negative indicates left rotation, positive indicates right rotation (default: 0.0) |
| `roll` | FLOAT | No | -10.0 to 10.0 | Controls camera's rolling amount (z-axis). Negative indicates counterclockwise, positive indicates clockwise (default: 0.0) |
| `zoom` | FLOAT | No | -10.0 to 10.0 | Controls change in camera's focal length. Negative indicates narrower field of view, positive indicates wider field of view (default: 0.0) |

**Note:** At least one of the camera control parameters (`horizontal_movement`, `vertical_movement`, `pan`, `tilt`, `roll`, or `zoom`) must have a non-zero value for the configuration to be valid.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `camera_control` | CAMERA_CONTROL | Returns the configured camera control settings for use in video generation |
