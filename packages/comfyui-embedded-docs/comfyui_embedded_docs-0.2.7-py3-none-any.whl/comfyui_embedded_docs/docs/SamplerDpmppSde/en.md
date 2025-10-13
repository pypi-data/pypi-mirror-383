
This node is designed to generate a sampler for the DPM++ SDE (Stochastic Differential Equation) model. It adapts to both CPU and GPU execution environments, optimizing the sampler's implementation based on the available hardware.

## Inputs

| Parameter      | Data Type | Description |
|----------------|-------------|-------------|
| `eta`          | FLOAT       | Specifies the step size for the SDE solver, influencing the granularity of the sampling process.|
| `s_noise`      | FLOAT       | Determines the level of noise to be applied during the sampling process, affecting the diversity of the generated samples.|
| `r`            | FLOAT       | Controls the ratio of noise reduction in the sampling process, impacting the clarity and quality of the generated samples.|
| `noise_device` | COMBO[STRING]| Selects the execution environment (CPU or GPU) for the sampler, optimizing performance based on available hardware.|

## Outputs

| Parameter    | Data Type | Description |
|----------------|-------------|-------------|
| `sampler`    | SAMPLER     | The generated sampler configured with the specified parameters, ready for use in sampling operations. |
