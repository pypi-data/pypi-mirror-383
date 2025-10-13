
The RepeatLatentBatch node is designed to replicate a given batch of latent representations a specified number of times, potentially including additional data like noise masks and batch indices. This functionality is crucial for operations that require multiple instances of the same latent data, such as data augmentation or specific generative tasks.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `samples` | `LATENT`    | The 'samples' parameter represents the latent representations to be replicated. It is essential for defining the data that will undergo repetition. |
| `amount`  | `INT`       | The 'amount' parameter specifies the number of times the input samples should be repeated. It directly influences the size of the output batch, thereby affecting the computational load and the diversity of the generated data. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The output is a modified version of the input latent representations, replicated according to the specified 'amount'. It may include replicated noise masks and adjusted batch indices, if applicable. |
