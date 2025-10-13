The LatentBatchSeedBehavior node is designed to modify the seed behavior of a batch of latent samples. It allows for either randomizing or fixing the seed across the batch, thereby influencing the generation process by either introducing variability or maintaining consistency in the generated outputs.

## Inputs

| Parameter       | Data Type | Description |
|-----------------|--------------|-------------|
| `samples`       | `LATENT`     | The 'samples' parameter represents the batch of latent samples to be processed. Its modification depends on the seed behavior chosen, affecting the consistency or variability of the generated outputs. |
| `seed_behavior`  | COMBO[STRING] | The 'seed_behavior' parameter dictates whether the seed for the batch of latent samples should be randomized or fixed. This choice significantly impacts the generation process by either introducing variability or ensuring consistency across the batch. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The output is a modified version of the input latent samples, with adjustments made based on the specified seed behavior. It either maintains or alters the batch index to reflect the chosen seed behavior. |
