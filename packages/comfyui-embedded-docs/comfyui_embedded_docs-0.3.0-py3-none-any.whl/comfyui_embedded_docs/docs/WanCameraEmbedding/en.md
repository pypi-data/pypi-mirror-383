> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanCameraEmbedding/en.md)

The WanCameraEmbedding node generates camera trajectory embeddings using Plücker embeddings based on camera motion parameters. It creates a sequence of camera poses that simulate different camera movements and converts them into embedding tensors suitable for video generation pipelines.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `camera_pose` | COMBO | Yes | "Static"<br>"Pan Up"<br>"Pan Down"<br>"Pan Left"<br>"Pan Right"<br>"Zoom In"<br>"Zoom Out"<br>"Anti Clockwise (ACW)"<br>"ClockWise (CW)" | The type of camera movement to simulate (default: "Static") |
| `width` | INT | Yes | 16 to MAX_RESOLUTION | The width of the output in pixels (default: 832, step: 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | The height of the output in pixels (default: 480, step: 16) |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | The length of the camera trajectory sequence (default: 81, step: 4) |
| `speed` | FLOAT | No | 0.0 to 10.0 | The speed of the camera movement (default: 1.0, step: 0.1) |
| `fx` | FLOAT | No | 0.0 to 1.0 | The focal length x parameter (default: 0.5, step: 0.000000001) |
| `fy` | FLOAT | No | 0.0 to 1.0 | The focal length y parameter (default: 0.5, step: 0.000000001) |
| `cx` | FLOAT | No | 0.0 to 1.0 | The principal point x coordinate (default: 0.5, step: 0.01) |
| `cy` | FLOAT | No | 0.0 to 1.0 | The principal point y coordinate (default: 0.5, step: 0.01) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `camera_embedding` | TENSOR | The generated camera embedding tensor containing the trajectory sequence |
| `width` | INT | The width value that was used for processing |
| `height` | INT | The height value that was used for processing |
| `length` | INT | The length value that was used for processing |
