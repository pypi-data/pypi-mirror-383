The `EmptyLatentImage` node is designed to generate a blank latent space representation with specified dimensions and batch size. This node serves as a foundational step in generating or manipulating images in latent space, providing a starting point for further image synthesis or modification processes.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `width`   | `INT`       | Specifies the width of the latent image to be generated. This parameter directly influences the spatial dimensions of the resulting latent representation. |
| `height`  | `INT`       | Determines the height of the latent image to be generated. This parameter is crucial for defining the spatial dimensions of the latent space representation. |
| `batch_size` | `INT` | Controls the number of latent images to be generated in a single batch. This allows for the generation of multiple latent representations simultaneously, facilitating batch processing. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The output is a tensor representing a batch of blank latent images, serving as a base for further image generation or manipulation in latent space. |
