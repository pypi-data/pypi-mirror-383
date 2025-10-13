El nodo `FeatherMask` aplica un efecto de desvanecimiento a los bordes de una máscara dada, haciendo una transición suave de los bordes de la máscara al ajustar su opacidad según las distancias especificadas desde cada borde. Esto crea un efecto de borde más suave y difuminado.

## Entradas

| Parámetro | Data Type | Descripción |
|-----------|--------------|-------------|
| `máscara`    | MASK         | La máscara a la que se aplicará el efecto de desvanecimiento. Determina el área de la imagen que se verá afectada por el desvanecimiento. |
| `izquierda`    | INT          | Especifica la distancia desde el borde izquierdo dentro de la cual se aplicará el efecto de desvanecimiento. |
| `arriba`     | INT          | Especifica la distancia desde el borde superior dentro de la cual se aplicará el efecto de desvanecimiento. |
| `derecha`   | INT          | Especifica la distancia desde el borde derecho dentro de la cual se aplicará el efecto de desvanecimiento. |
| `abajo`  | INT          | Especifica la distancia desde el borde inferior dentro de la cual se aplicará el efecto de desvanecimiento. |

## Salidas

| Parámetro | Data Type | Descripción |
|-----------|--------------|-------------|
| `máscara`    | MASK         | La salida es una versión modificada de la máscara de entrada con un efecto de desvanecimiento aplicado a sus bordes. |
