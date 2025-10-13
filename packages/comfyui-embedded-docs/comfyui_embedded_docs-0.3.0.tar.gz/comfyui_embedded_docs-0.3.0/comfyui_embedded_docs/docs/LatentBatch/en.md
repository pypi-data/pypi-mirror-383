The LatentBatch node is designed to merge two sets of latent samples into a single batch, potentially resizing one set to match the dimensions of the other before concatenation. This operation facilitates the combination of different latent representations for further processing or generation tasks.

## Inputs

| Parameter    | Data Type | Description |
|--------------|-------------|-------------|
| `samples1`   | `LATENT`    | The first set of latent samples to be merged. It plays a crucial role in determining the final shape of the merged batch. |
| `samples2`   | `LATENT`    | The second set of latent samples to be merged. If its dimensions differ from the first set, it is resized to ensure compatibility before merging. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The merged set of latent samples, now combined into a single batch for further processing. |
