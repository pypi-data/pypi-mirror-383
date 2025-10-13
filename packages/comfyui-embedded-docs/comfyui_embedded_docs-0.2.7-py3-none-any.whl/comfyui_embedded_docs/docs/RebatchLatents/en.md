
The RebatchLatents node is designed to reorganize a batch of latent representations into a new batch configuration, based on a specified batch size. It ensures that the latent samples are grouped appropriately, handling variations in dimensions and sizes, to facilitate further processing or model inference.

## Inputs

| Parameter    | Data Type | Description |
|--------------|-------------|-------------|
| `latents`    | `LATENT`    | The 'latents' parameter represents the input latent representations to be rebatched. It is crucial for determining the structure and content of the output batch. |
| `batch_size` | `INT`      | The 'batch_size' parameter specifies the desired number of samples per batch in the output. It directly influences the grouping and division of the input latents into new batches. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The output is a reorganized batch of latent representations, adjusted according to the specified batch size. It facilitates further processing or analysis. |
