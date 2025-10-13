
The LatentInterpolate node is designed to perform interpolation between two sets of latent samples based on a specified ratio, blending the characteristics of both sets to produce a new, intermediate set of latent samples.

## Inputs

| Parameter    | Data Type | Description |
|--------------|-------------|-------------|
| `samples1`   | `LATENT`    | The first set of latent samples to be interpolated. It serves as the starting point for the interpolation process. |
| `samples2`   | `LATENT`    | The second set of latent samples to be interpolated. It serves as the endpoint for the interpolation process. |
| `ratio`      | `FLOAT`     | A floating-point value that determines the weight of each set of samples in the interpolated output. A ratio of 0 produces a copy of the first set, while a ratio of 1 produces a copy of the second set. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The output is a new set of latent samples that represent an interpolated state between the two input sets, based on the specified ratio. |
