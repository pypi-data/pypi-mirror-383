
The VideoLinearCFGGuidance node applies a linear conditioning guidance scale to a video model, adjusting the influence of conditioned and unconditioned components over a specified range. This enables dynamic control over the generation process, allowing for fine-tuning of the model's output based on the desired level of conditioning.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `model`   | MODEL     | The model parameter represents the video model to which the linear CFG guidance will be applied. It is crucial for defining the base model that will be modified with the guidance scale. |
| `min_cfg` | `FLOAT`     | The min_cfg parameter specifies the minimum conditioning guidance scale to be applied, serving as the starting point for the linear scale adjustment. It plays a key role in determining the lower bound of the guidance scale, influencing the model's output. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `model`   | MODEL     | The output is a modified version of the input model, with the linear CFG guidance scale applied. This adjusted model is capable of generating outputs with varying degrees of conditioning, based on the specified guidance scale. |
