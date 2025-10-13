The KarrasScheduler node is designed to generate a sequence of noise levels (sigmas) based on the Karras et al. (2022) noise schedule. This scheduler is useful for controlling the diffusion process in generative models, allowing for fine-tuned adjustments to the noise levels applied at each step of the generation process.

## Inputs

| Parameter   | Data Type | Description                                                                                      |
|-------------|-------------|------------------------------------------------------------------------------------------------|
| `steps`     | INT         | Specifies the number of steps in the noise schedule, affecting the granularity of the generated sigmas sequence. |
| `sigma_max` | FLOAT       | The maximum sigma value in the noise schedule, setting the upper bound of noise levels.                    |
| `sigma_min` | FLOAT       | The minimum sigma value in the noise schedule, setting the lower bound of noise levels.                    |
| `rho`       | FLOAT       | A parameter that controls the shape of the noise schedule curve, influencing how noise levels progress from sigma_min to sigma_max. |

## Outputs

| Parameter | Data Type | Description                                                                 |
|-----------|-------------|-----------------------------------------------------------------------------|
| `sigmas`  | SIGMAS      | The generated sequence of noise levels (sigmas) following the Karras et al. (2022) noise schedule. |
