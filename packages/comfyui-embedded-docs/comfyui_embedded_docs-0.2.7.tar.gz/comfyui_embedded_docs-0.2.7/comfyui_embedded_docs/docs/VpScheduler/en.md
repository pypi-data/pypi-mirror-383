
The VPScheduler node is designed to generate a sequence of noise levels (sigmas) based on the Variance Preserving (VP) scheduling method. This sequence is crucial for guiding the denoising process in diffusion models, allowing for controlled generation of images or other data types.

## Inputs

| Parameter   | Data Type | Description                                                                                                                                      |
|-------------|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| `steps`     | INT         | Specifies the number of steps in the diffusion process, affecting the granularity of the generated noise levels.                              |
| `beta_d`    | FLOAT       | Determines the overall noise level distribution, influencing the variance of the generated noise levels.                                 |
| `beta_min`  | FLOAT       | Sets the minimum boundary for the noise level, ensuring the noise does not fall below a certain threshold.                              |
| `eps_s`     | FLOAT       | Adjusts the starting epsilon value, fine-tuning the initial noise level in the diffusion process.                                    |

## Outputs

| Parameter   | Data Type | Description                                                                                   |
|-------------|-------------|-----------------------------------------------------------------------------------------------|
| `sigmas`    | SIGMAS      | A sequence of noise levels (sigmas) generated based on the VP scheduling method, used to guide the denoising process in diffusion models. |
