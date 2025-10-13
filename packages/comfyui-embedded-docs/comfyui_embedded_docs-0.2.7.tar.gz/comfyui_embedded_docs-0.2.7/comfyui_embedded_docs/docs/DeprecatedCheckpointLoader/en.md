The CheckpointLoader node is designed for advanced loading operations, specifically to load model checkpoints along with their configurations. It facilitates the retrieval of model components necessary for initializing and running generative models, including configurations and checkpoints from specified directories.

## Inputs

| Parameter    | Data Type | Description |
|--------------|--------------|-------------|
| `config_name` | COMBO[STRING] | Specifies the name of the configuration file to be used. This is crucial for determining the model's parameters and settings, affecting the model's behavior and performance. |
| `ckpt_name`  | COMBO[STRING] | Indicates the name of the checkpoint file to be loaded. This directly influences the state of the model being initialized, impacting its initial weights and biases. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `model`   | MODEL     | Represents the primary model loaded from the checkpoint, ready for further operations or inference. |
| `clip`    | CLIP      | Provides the CLIP model component, if available and requested, loaded from the checkpoint. |
| `vae`     | VAE       | Delivers the VAE model component, if available and requested, loaded from the checkpoint. |
