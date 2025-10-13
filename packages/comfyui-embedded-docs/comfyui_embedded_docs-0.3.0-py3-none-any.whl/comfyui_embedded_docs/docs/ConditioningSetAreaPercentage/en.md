The ConditioningSetAreaPercentage node specializes in adjusting the area of influence for conditioning elements based on percentage values. It allows for the specification of the area's dimensions and position as percentages of the total image size, alongside a strength parameter to modulate the intensity of the conditioning effect.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `CONDITIONING` | CONDITIONING | Represents the conditioning elements to be modified, serving as the foundation for applying area and strength adjustments. |
| `width`   | `FLOAT`     | Specifies the width of the area as a percentage of the total image width, influencing how much of the image the conditioning affects horizontally. |
| `height`  | `FLOAT`     | Determines the height of the area as a percentage of the total image height, affecting the vertical extent of the conditioning's influence. |
| `x`       | `FLOAT`     | Indicates the horizontal starting point of the area as a percentage of the total image width, positioning the conditioning effect. |
| `y`       | `FLOAT`     | Specifies the vertical starting point of the area as a percentage of the total image height, positioning the conditioning effect. |
| `strength`| `FLOAT`     | Controls the intensity of the conditioning effect within the specified area, allowing for fine-tuning of its impact. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `CONDITIONING` | CONDITIONING | Returns the modified conditioning elements with updated area and strength parameters, ready for further processing or application. |
