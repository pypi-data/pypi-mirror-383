
The SplitSigmas node is designed for dividing a sequence of sigma values into two parts based on a specified step. This functionality is crucial for operations that require different handling or processing of the initial and subsequent parts of the sigma sequence, enabling more flexible and targeted manipulation of these values.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `sigmas`  | `SIGMAS`    | The 'sigmas' parameter represents the sequence of sigma values to be split. It is essential for determining the division point and the resulting two sequences of sigma values, impacting the node's execution and results. |
| `step`    | `INT`       | The 'step' parameter specifies the index at which the sigma sequence should be split. It plays a critical role in defining the boundary between the two resulting sigma sequences, influencing the node's functionality and the characteristics of the output. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `sigmas`  | `SIGMAS`    | The node outputs two sequences of sigma values, each representing a part of the original sequence divided at the specified step. These outputs are crucial for subsequent operations that require differentiated handling of sigma values. |
