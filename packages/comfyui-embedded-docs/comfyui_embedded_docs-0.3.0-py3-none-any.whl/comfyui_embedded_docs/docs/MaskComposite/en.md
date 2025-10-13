
This node specializes in combining two mask inputs through a variety of operations such as addition, subtraction, and logical operations, to produce a new, modified mask. It abstractly handles the manipulation of mask data to achieve complex masking effects, serving as a crucial component in mask-based image editing and processing workflows.

## Inputs

| Parameter    | Data Type | Description                                                                                                                                      |
| ------------ | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `destination`| MASK        | The primary mask that will be modified based on the operation with the source mask. It plays a central role in the composite operation, acting as the base for modifications. |
| `source`     | MASK        | The secondary mask that will be used in conjunction with the destination mask to perform the specified operation, influencing the final output mask. |
| `x`          | INT         | The horizontal offset at which the source mask will be applied to the destination mask, affecting the positioning of the composite result.       |
| `y`          | INT         | The vertical offset at which the source mask will be applied to the destination mask, affecting the positioning of the composite result.         |
| `operation`  | COMBO[STRING]| Specifies the type of operation to apply between the destination and source masks, such as 'add', 'subtract', or logical operations, determining the nature of the composite effect. |

## Outputs

| Parameter | Data Type | Description                                                                 |
| --------- | ------------ | ---------------------------------------------------------------------------- |
| `mask`    | MASK        | The resulting mask after applying the specified operation between the destination and source masks, representing the composite outcome. |
