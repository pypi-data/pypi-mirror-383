
The ModelMergeAdd node is designed for merging two models by adding key patches from one model to another. This process involves cloning the first model and then applying patches from the second model, allowing for the combination of features or behaviors from both models.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `model1`  | `MODEL`     | The first model to be cloned and to which patches from the second model will be added. It serves as the base model for the merging process. |
| `model2`  | `MODEL`     | The second model from which key patches are extracted and added to the first model. It contributes additional features or behaviors to the merged model. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `model`   | MODEL     | The result of merging two models by adding key patches from the second model to the first. This merged model combines features or behaviors from both models. |
