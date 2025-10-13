此节点设计用于连接条件向量，特别是将'conditioning_from'向量合并到'conditioning_to'向量中。在需要将来自两个源的条件信息组合成单一、统一表示的场景中，此操作是基础。

## 输入

| 参数名称 | 数据类型 | 作用 |
| --- | --- | --- |
| `条件到` | `CONDITIONING` | 表示'conditioning_from'向量将被连接到的主要条件向量集。它作为连接过程的基础。 |
| `条件从` | `CONDITIONING` | 包含要连接到'conditioning_to'向量的条件向量。此参数允许将额外的条件信息集成到现有的集。 |

## 输出

| 参数名称 | 数据类型 | 作用 |
| --- | --- | --- |
| `CONDITIONING` | CONDITIONING | 输出是统一的条件向量集，由'conditioning_from'向量连接到'conditioning_to'向量的结果。 |
