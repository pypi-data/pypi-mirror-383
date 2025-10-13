The `FlipSigmas` node is designed to manipulate the sequence of sigma values used in diffusion models by reversing their order and ensuring the first value is non-zero if originally zero. This operation is crucial for adapting the noise levels in reverse order, facilitating the generation process in models that operate by gradually reducing noise from data.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `sigmas`  | `SIGMAS`    | The 'sigmas' parameter represents the sequence of sigma values to be flipped. This sequence is crucial for controlling the noise levels applied during the diffusion process, and flipping it is essential for the reverse generation process. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `sigmas`  | `SIGMAS`    | The output is the modified sequence of sigma values, flipped and adjusted to ensure the first value is non-zero if originally zero, ready for use in subsequent diffusion model operations. |
