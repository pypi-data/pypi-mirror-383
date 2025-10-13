This node is designed to modify the conditioning information by setting specific areas within the conditioning context. It allows for the precise spatial manipulation of conditioning elements, enabling targeted adjustments and enhancements based on specified dimensions and strength.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `CONDITIONING` | CONDITIONING | The conditioning data to be modified. It serves as the base for applying spatial adjustments. |
| `width`   | `INT`      | Specifies the width of the area to be set within the conditioning context, influencing the horizontal scope of the adjustment. |
| `height`  | `INT`      | Determines the height of the area to be set, affecting the vertical extent of the conditioning modification. |
| `x`       | `INT`      | The horizontal starting point of the area to be set, positioning the adjustment within the conditioning context. |
| `y`       | `INT`      | The vertical starting point for the area adjustment, establishing its position within the conditioning context. |
| `strength`| `FLOAT`    | Defines the intensity of the conditioning modification within the specified area, allowing for nuanced control over the adjustment's impact. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `CONDITIONING` | CONDITIONING | The modified conditioning data, reflecting the specified area settings and adjustments. |
