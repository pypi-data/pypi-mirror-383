The CropMask node is designed for cropping a specified area from a given mask. It allows users to define the region of interest by specifying coordinates and dimensions, effectively extracting a portion of the mask for further processing or analysis.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `mask`    | MASK        | The mask input represents the mask image to be cropped. It is essential for defining the area to be extracted based on the specified coordinates and dimensions. |
| `x`       | INT         | The x coordinate specifies the starting point on the horizontal axis from which the cropping should begin. |
| `y`       | INT         | The y coordinate determines the starting point on the vertical axis for the cropping operation. |
| `width`   | INT         | Width defines the horizontal extent of the crop area from the starting point. |
| `height`  | INT         | Height specifies the vertical extent of the crop area from the starting point. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `mask`    | MASK        | The output is a cropped mask, which is a portion of the original mask defined by the specified coordinates and dimensions. |
