
The SamplerCustom node is designed to provide a flexible and customizable sampling mechanism for various applications. It enables users to select and configure different sampling strategies tailored to their specific needs, enhancing the adaptability and efficiency of the sampling process.

## Inputs

| Parameter | Data Type | Description |
|-----------|--------------|-------------|
| `model`   | `MODEL`      | The 'model' input type specifies the model to be used for sampling, playing a crucial role in determining the sampling behavior and output. |
| `add_noise` | `BOOLEAN`    | The 'add_noise' input type allows users to specify whether noise should be added to the sampling process, influencing the diversity and characteristics of the generated samples. |
| `noise_seed` | `INT`        | The 'noise_seed' input type provides a seed for the noise generation, ensuring reproducibility and consistency in the sampling process when adding noise. |
| `cfg`     | `FLOAT`      | The 'cfg' input type sets the configuration for the sampling process, allowing for fine-tuning of the sampling parameters and behavior. |
| `positive` | `CONDITIONING` | The 'positive' input type represents positive conditioning information, guiding the sampling process towards generating samples that align with specified positive attributes. |
| `negative` | `CONDITIONING` | The 'negative' input type represents negative conditioning information, steering the sampling process away from generating samples that exhibit specified negative attributes. |
| `sampler` | `SAMPLER`    | The 'sampler' input type selects the specific sampling strategy to be employed, directly impacting the nature and quality of the generated samples. |
| `sigmas`  | `SIGMAS`     | The 'sigmas' input type defines the noise levels to be used in the sampling process, affecting the exploration of the sample space and the diversity of the output. |
| `latent_image` | `LATENT` | The 'latent_image' input type provides an initial latent image for the sampling process, serving as a starting point for sample generation. |

## Outputs

| Parameter | Data Type | Description |
|-----------|--------------|-------------|
| `output`  | `LATENT`     | The 'output' represents the primary result of the sampling process, containing the generated samples. |
| `denoised_output` | `LATENT` | The 'denoised_output' represents the samples after a denoising process has been applied, potentially enhancing the clarity and quality of the generated samples. |
