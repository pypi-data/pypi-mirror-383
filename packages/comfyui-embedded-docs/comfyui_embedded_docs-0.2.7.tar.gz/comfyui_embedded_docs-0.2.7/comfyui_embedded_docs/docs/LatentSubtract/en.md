
The LatentSubtract node is designed for subtracting one latent representation from another. This operation can be used to manipulate or modify the characteristics of generative models' outputs by effectively removing features or attributes represented in one latent space from another.

## Inputs

| Parameter    | Data Type | Description |
|--------------|-------------|-------------|
| `samples1`   | `LATENT`    | The first set of latent samples to be subtracted from. It serves as the base for the subtraction operation. |
| `samples2`   | `LATENT`    | The second set of latent samples that will be subtracted from the first set. This operation can alter the resulting generative model's output by removing attributes or features. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The result of subtracting the second set of latent samples from the first. This modified latent representation can be used for further generative tasks. |
