The ConditioningConcat node is designed to concatenate conditioning vectors, specifically merging the 'conditioning_from' vector into the 'conditioning_to' vector. This operation is fundamental in scenarios where the conditioning information from two sources needs to be combined into a single, unified representation.

## Inputs

| Parameter             | Comfy dtype        | Description |
|-----------------------|--------------------|-------------|
| `conditioning_to`     | `CONDITIONING`     | Represents the primary set of conditioning vectors to which the 'conditioning_from' vectors will be concatenated. It serves as the base for the concatenation process. |
| `conditioning_from`   | `CONDITIONING`     | Consists of conditioning vectors that are to be concatenated to the 'conditioning_to' vectors. This parameter allows for additional conditioning information to be integrated into the existing set. |

## Outputs

| Parameter            | Comfy dtype        | Description |
|----------------------|--------------------|-------------|
| `conditioning`       | `CONDITIONING`     | The output is a unified set of conditioning vectors, resulting from the concatenation of 'conditioning_from' vectors into the 'conditioning_to' vectors. |
