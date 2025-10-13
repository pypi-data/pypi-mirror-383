The `ExponentialScheduler` node is designed to generate a sequence of sigma values following an exponential schedule for diffusion sampling processes. It provides a customizable approach to control the noise levels applied at each step of the diffusion process, allowing for fine-tuning of the sampling behavior.

## Inputs

| Parameter   | Data Type | Description                                                                                   |
|-------------|-------------|---------------------------------------------------------------------------------------------|
| `steps`     | INT         | Specifies the number of steps in the diffusion process. It influences the length of the generated sigma sequence and thus the granularity of the noise application. |
| `sigma_max` | FLOAT       | Defines the maximum sigma value, setting the upper limit of noise intensity in the diffusion process. It plays a crucial role in determining the range of noise levels applied. |
| `sigma_min` | FLOAT       | Sets the minimum sigma value, establishing the lower boundary of noise intensity. This parameter helps in fine-tuning the starting point of the noise application. |

## Outputs

| Parameter | Data Type | Description                                                                                   |
|-----------|-------------|---------------------------------------------------------------------------------------------|
| `sigmas`  | SIGMAS      | A sequence of sigma values generated according to the exponential schedule. These values are used to control the noise levels at each step of the diffusion process. |
