The `ImageCrop` node is designed for cropping images to a specified width and height starting from a given x and y coordinate. This functionality is essential for focusing on specific regions of an image or for adjusting the image size to meet certain requirements.

## Inputs

| Field | Data Type | Description                                                                                   |
|-------|-------------|-----------------------------------------------------------------------------------------------|
| `image` | `IMAGE` | The input image to be cropped. This parameter is crucial as it defines the source image from which a region will be extracted based on the specified dimensions and coordinates. |
| `width` | `INT` | Specifies the width of the cropped image. This parameter determines how wide the resulting cropped image will be. |
| `height` | `INT` | Specifies the height of the cropped image. This parameter determines the height of the resulting cropped image. |
| `x` | `INT` | The x-coordinate of the top-left corner of the cropping area. This parameter sets the starting point for the width dimension of the crop. |
| `y` | `INT` | The y-coordinate of the top-left corner of the cropping area. This parameter sets the starting point for the height dimension of the crop. |

## Outputs

| Field | Data Type | Description                                                                   |
|-------|-------------|-------------------------------------------------------------------------------|
| `image` | `IMAGE` | The cropped image as a result of the cropping operation. This output is significant for further processing or analysis of the specified image region. |
