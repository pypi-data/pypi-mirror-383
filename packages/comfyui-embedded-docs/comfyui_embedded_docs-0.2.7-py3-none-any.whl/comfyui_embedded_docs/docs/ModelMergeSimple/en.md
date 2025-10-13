The ModelMergeSimple node is designed for merging two models by blending their parameters based on a specified ratio. This node facilitates the creation of hybrid models that combine the strengths or characteristics of both input models.

The `ratio` parameter determines the blending ratio between the two models. When this value is 1, the output model is 100% `model1`, and when this value is 0, the output model is 100% `model2`.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `model1`  | `MODEL`     | The first model to be merged. It serves as the base model onto which patches from the second model are applied. |
| `model2`  | `MODEL`     | The second model whose patches are applied onto the first model, influenced by the specified ratio. |
| `ratio`   | `FLOAT`     | When this value is 1, the output model is 100% `model1`, and when this value is 0, the output model is 100% `model2`. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `model`   | MODEL     | The resulting merged model, incorporating elements from both input models according to the specified ratio. |
