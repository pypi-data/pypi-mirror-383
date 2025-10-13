This node zeroes out specific elements within the conditioning data structure, effectively neutralizing their influence in subsequent processing steps. It's designed for advanced conditioning operations where direct manipulation of the conditioning's internal representation is required.

## Inputs

| Parameter | Comfy dtype                | Description |
|-----------|----------------------------|-------------|
| `CONDITIONING` | CONDITIONING | The conditioning data structure to be modified. This node zeroes out the 'pooled_output' elements within each conditioning entry, if present. |

## Outputs

| Parameter | Comfy dtype                | Description |
|-----------|----------------------------|-------------|
| `CONDITIONING` | CONDITIONING | The modified conditioning data structure, with 'pooled_output' elements set to zero where applicable. |
