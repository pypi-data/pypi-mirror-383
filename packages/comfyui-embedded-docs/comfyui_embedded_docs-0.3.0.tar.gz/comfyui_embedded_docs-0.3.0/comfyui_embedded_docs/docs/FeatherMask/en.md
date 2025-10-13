The `FeatherMask` node applies a feathering effect to the edges of a given mask, smoothly transitioning the mask's edges by adjusting their opacity based on specified distances from each edge. This creates a softer, more blended edge effect.

## Inputs

| Parameter | Data Type | Description |
|-----------|--------------|-------------|
| `mask`    | MASK         | The mask to which the feathering effect will be applied. It determines the area of the image that will be affected by the feathering. |
| `left`    | INT          | Specifies the distance from the left edge within which the feathering effect will be applied. |
| `top`     | INT          | Specifies the distance from the top edge within which the feathering effect will be applied. |
| `right`   | INT          | Specifies the distance from the right edge within which the feathering effect will be applied. |
| `bottom`  | INT          | Specifies the distance from the bottom edge within which the feathering effect will be applied. |

## Outputs

| Parameter | Data Type | Description |
|-----------|--------------|-------------|
| `mask`    | MASK         | The output is a modified version of the input mask with a feathering effect applied to its edges. |
