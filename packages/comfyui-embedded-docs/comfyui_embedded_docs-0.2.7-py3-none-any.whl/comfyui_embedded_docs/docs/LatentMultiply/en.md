
The LatentMultiply node is designed to scale the latent representation of samples by a specified multiplier. This operation allows for the adjustment of the intensity or magnitude of features within the latent space, enabling fine-tuning of generated content or the exploration of variations within a given latent direction.

## Inputs

| Parameter    | Data Type | Description |
|--------------|-------------|-------------|
| `samples`    | `LATENT`    | The 'samples' parameter represents the latent representations to be scaled. It is crucial for defining the input data on which the multiplication operation will be performed. |
| `multiplier` | `FLOAT`     | The 'multiplier' parameter specifies the scaling factor to be applied to the latent samples. It plays a key role in adjusting the magnitude of the latent features, allowing for nuanced control over the generated output. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The output is a modified version of the input latent samples, scaled by the specified multiplier. This allows for the exploration of variations within the latent space by adjusting the intensity of its features. |
