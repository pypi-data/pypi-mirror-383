
This node is designed to generate a sampler for the DPMPP_2M_SDE model, allowing for the creation of samples based on specified solver types, noise levels, and computational device preferences. It abstracts the complexities of sampler configuration, providing a streamlined interface for generating samples with customized settings.

## Inputs

| Parameter       | Data Type | Description                                                                 |
|-----------------|-------------|-----------------------------------------------------------------------------|
| `solver_type`   | COMBO[STRING] | Specifies the solver type to be used in the sampling process, offering options between 'midpoint' and 'heun'. This choice influences the numerical integration method applied during sampling. |
| `eta`           | `FLOAT`     | Determines the step size in the numerical integration, affecting the granularity of the sampling process. A higher value indicates a larger step size. |
| `s_noise`       | `FLOAT`     | Controls the level of noise introduced during the sampling process, influencing the variability of the generated samples. |
| `noise_device`  | COMBO[STRING] | Indicates the computational device ('gpu' or 'cpu') on which the noise generation process is executed, affecting performance and efficiency. |

## Outputs

| Parameter       | Data Type | Description                                                                 |
|-----------------|-------------|-----------------------------------------------------------------------------|
| `sampler`       | `SAMPLER`   | The output is a sampler configured according to the specified parameters, ready for generating samples. |
