
This node is designed to extract a specific subset of latent samples from a given batch based on the specified batch index and length. It allows for selective processing of latent samples, facilitating operations on smaller segments of the batch for efficiency or targeted manipulation.

## Inputs

| Parameter     | Data Type | Description |
|---------------|-------------|-------------|
| `samples`     | `LATENT`    | The collection of latent samples from which a subset will be extracted. This parameter is crucial for determining the source batch of samples to be processed. |
| `batch_index` | `INT`       | Specifies the starting index within the batch from which the subset of samples will begin. This parameter enables targeted extraction of samples from specific positions in the batch. |
| `length`      | `INT`       | Defines the number of samples to be extracted from the specified starting index. This parameter controls the size of the subset to be processed, allowing for flexible manipulation of batch segments. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The extracted subset of latent samples, now available for further processing or analysis. |
