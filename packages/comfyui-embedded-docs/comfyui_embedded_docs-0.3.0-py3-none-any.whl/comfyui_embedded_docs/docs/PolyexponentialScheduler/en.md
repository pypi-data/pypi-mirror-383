
The PolyexponentialScheduler node is designed to generate a sequence of noise levels (sigmas) based on a polyexponential noise schedule. This schedule is a polynomial function in the logarithm of sigma, allowing for a flexible and customizable progression of noise levels throughout the diffusion process.

## Inputs

| Parameter   | Data Type | Description                                                                                                                                                                                                                                                                                                                                                      |
|-------------|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `steps`     | INT         | Specifies the number of steps in the diffusion process, affecting the granularity of the generated noise levels.                                                                                                                                                                                                                                                                        |
| `sigma_max` | FLOAT       | The maximum noise level, setting the upper bound of the noise schedule.                                                                                                                                                                                                                                                                                                                                 |
| `sigma_min` | FLOAT       | The minimum noise level, setting the lower bound of the noise schedule.                                                                                                                                                                                                                                                                                                                                 |
| `rho`       | FLOAT       | A parameter that controls the shape of the polyexponential noise schedule, influencing how noise levels progress between the minimum and maximum values.                                                                                                                                                                                                               |

## Outputs

| Parameter | Data Type | Description                                                                 |
|-----------|-------------|-----------------------------------------------------------------------------|
| `sigmas`  | SIGMAS      | The output is a sequence of noise levels (sigmas) tailored to the specified polyexponential noise schedule. |
