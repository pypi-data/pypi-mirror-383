
ModelMergeBlocks is designed for advanced model merging operations, allowing for the integration of two models with customizable blending ratios for different parts of the models. This node facilitates the creation of hybrid models by selectively merging components from two source models based on specified parameters.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `model1`  | `MODEL`     | The first model to be merged. It serves as the base model onto which patches from the second model are applied. |
| `model2`  | `MODEL`     | The second model from which patches are extracted and applied to the first model, based on the specified blending ratios. |
| `input`   | `FLOAT`     | Specifies the blending ratio for the input layer of the models. It determines how much of the second model's input layer is merged into the first model. |
| `middle`  | `FLOAT`     | Defines the blending ratio for the middle layers of the models. This parameter controls the integration level of the models' middle layers. |
| `out`     | `FLOAT`     | Determines the blending ratio for the output layer of the models. It affects the final output by adjusting the contribution of the second model's output layer. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `model`   | MODEL     | The resulting merged model, which is a hybrid of the two input models with patches applied according to the specified blending ratios. |
