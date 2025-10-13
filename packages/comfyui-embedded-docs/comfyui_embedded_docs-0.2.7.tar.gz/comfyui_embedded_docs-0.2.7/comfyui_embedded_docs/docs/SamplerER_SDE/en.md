> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerER_SDE/en.md)

The SamplerER_SDE node provides specialized sampling methods for diffusion models, offering different solver types including ER-SDE, Reverse-time SDE, and ODE approaches. It allows control over the stochastic behavior and computational stages of the sampling process. The node automatically adjusts parameters based on the selected solver type to ensure proper functionality.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `solver_type` | COMBO | Yes | "ER-SDE"<br>"Reverse-time SDE"<br>"ODE" | The type of solver to use for sampling. Determines the mathematical approach for the diffusion process. |
| `max_stage` | INT | Yes | 1-3 | The maximum number of stages for the sampling process (default: 3). Controls the computational complexity and quality. |
| `eta` | FLOAT | Yes | 0.0-100.0 | Stochastic strength of reverse-time SDE (default: 1.0). When eta=0, it reduces to deterministic ODE. This setting doesn't apply to ER-SDE solver type. |
| `s_noise` | FLOAT | Yes | 0.0-100.0 | Noise scaling factor for the sampling process (default: 1.0). Controls the amount of noise applied during sampling. |

**Parameter Constraints:**

- When `solver_type` is set to "ODE" or when using "Reverse-time SDE" with `eta`=0, both `eta` and `s_noise` are automatically set to 0 regardless of user input values.
- The `eta` parameter only affects "Reverse-time SDE" solver type and has no effect on "ER-SDE" solver type.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | A configured sampler object that can be used in the sampling pipeline with the specified solver settings. |
