
This node is designed to process and condition data for use in StableZero123 models, focusing on preparing the input in a specific format that is compatible and optimized for these models.

## Inputs

| Parameter             | Comfy dtype        | Description |
|-----------------------|--------------------|-------------|
| `clip_vision`         | `CLIP_VISION`      | Processes visual data to align with the model's requirements, enhancing the model's understanding of visual context. |
| `init_image`          | `IMAGE`            | Serves as the initial image input for the model, setting the baseline for further image-based operations. |
| `vae`                 | `VAE`              | Integrates variational autoencoder outputs, facilitating the model's ability to generate or modify images. |
| `width`               | `INT`              | Specifies the width of the output image, allowing for dynamic resizing according to model needs. |
| `height`              | `INT`              | Determines the height of the output image, enabling customization of the output dimensions. |
| `batch_size`          | `INT`              | Controls the number of images processed in a single batch, optimizing computational efficiency. |
| `elevation`           | `FLOAT`            | Adjusts the elevation angle for 3D model rendering, enhancing the model's spatial understanding. |
| `azimuth`             | `FLOAT`            | Modifies the azimuth angle for 3D model visualization, improving the model's perception of orientation. |

## Outputs

| Parameter     | Data Type | Description |
|---------------|--------------|-------------|
| `positive`    | `CONDITIONING` | Generates positive conditioning vectors, aiding in the model's positive feature reinforcement. |
| `negative`    | `CONDITIONING` | Produces negative conditioning vectors, assisting in the model's avoidance of certain features. |
| `latent`      | `LATENT`     | Creates latent representations, facilitating deeper model insights into the data. |
