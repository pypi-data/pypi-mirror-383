This node is designed to modify the conditioning of a generative model by applying a mask with a specified strength to certain areas. It allows for targeted adjustments within the conditioning, enabling more precise control over the generation process.

## Inputs

### Required

| Parameter     | Data Type | Description |
|---------------|--------------|-------------|
| `CONDITIONING` | CONDITIONING | The conditioning data to be modified. It serves as the basis for applying the mask and strength adjustments. |
| `mask`        | `MASK`       | A mask tensor that specifies the areas within the conditioning to be modified. |
| `strength`    | `FLOAT`      | The strength of the mask's effect on the conditioning, allowing for fine-tuning of the applied modifications. |
| `set_cond_area` | COMBO[STRING] | Determines whether the mask's effect is applied to the default area or bounded by the mask itself, offering flexibility in targeting specific regions. |

## Outputs

| Parameter     | Data Type | Description |
|---------------|--------------|-------------|
| `CONDITIONING` | CONDITIONING | The modified conditioning data, with the mask and strength adjustments applied. |
