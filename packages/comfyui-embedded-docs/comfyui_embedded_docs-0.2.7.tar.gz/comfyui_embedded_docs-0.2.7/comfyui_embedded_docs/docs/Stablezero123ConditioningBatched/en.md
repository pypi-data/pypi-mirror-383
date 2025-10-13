
This node is designed to process conditioning information in a batched manner specifically tailored for the StableZero123 model. It focuses on efficiently handling multiple sets of conditioning data simultaneously, optimizing the workflow for scenarios where batch processing is crucial.

## Inputs

| Parameter             | Data Type | Description |
|----------------------|--------------|-------------|
| `clip_vision`         | `CLIP_VISION` | The CLIP vision embeddings that provide visual context for the conditioning process. |
| `init_image`          | `IMAGE`      | The initial image to be conditioned upon, serving as a starting point for the generation process. |
| `vae`                 | `VAE`        | The variational autoencoder used for encoding and decoding images in the conditioning process. |
| `width`               | `INT`        | The width of the output image. |
| `height`              | `INT`        | The height of the output image. |
| `batch_size`          | `INT`        | The number of conditioning sets to be processed in a single batch. |
| `elevation`           | `FLOAT`      | The elevation angle for 3D model conditioning, affecting the perspective of the generated image. |
| `azimuth`             | `FLOAT`      | The azimuth angle for 3D model conditioning, affecting the orientation of the generated image. |
| `elevation_batch_increment` | `FLOAT` | The incremental change in elevation angle across the batch, allowing for varied perspectives. |
| `azimuth_batch_increment` | `FLOAT` | The incremental change in azimuth angle across the batch, allowing for varied orientations. |

## Outputs

| Parameter     | Data Type | Description |
|---------------|--------------|-------------|
| `positive`    | `CONDITIONING` | The positive conditioning output, tailored for promoting certain features or aspects in the generated content. |
| `negative`    | `CONDITIONING` | The negative conditioning output, tailored for demoting certain features or aspects in the generated content. |
| `latent`      | `LATENT`     | The latent representation derived from the conditioning process, ready for further processing or generation steps. |
