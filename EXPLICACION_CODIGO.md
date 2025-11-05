# 📚 Análisis Técnico y Decisiones de Diseño

## 🎯 Introducción

El objectivo de este proyecto era crear un programa en python  para ayudar a la tienda`PyTech Store`a manejar sus ventas .lo que hace el programa es leer dos archivos  CSV: uno con la lista de productos y otro con las ventas que se quieren hacer .despues revisa cada venta para ver si hay stock y si el producto existe .al final ,crea dos archivos  nuevos un CSV con el inventario actualizado  y un reporte de texto que dice cuanto se gano y que ventas no se pudieron hacer .

---

## 📦 Importación de Módulos

```python
import csv
```

**¿Qué hace?**
- Importa el módulo `csv` que nos permite leer y escribir archivos CSV (Comma-Separated Values)
- Este módulo viene incluido con Python, no necesitas instalarlo

---

## 1. Carga de Datos: `leer_productos()` y `leer_ventas()`

### Decisión de Diseño: Elección de Estructuras de Datos

#### `leer_productos()` -> Diccionario
- **Problema:** Necesitaba una forma eficiente y buena de buscar la información de un producto (precio, stock) a partir de su `id_producto` durante el procesamiento de ventas.
- **Solución:** Se eligió un **diccionario** de Python.
  - **Justificación:** Los diccionarios ofrecen una  gran búsqueda de tiempo constante (O(1)) por clave. Usar el `id_producto` como clave (`productos['PROD001']`) es mucho más rápido y limpio que iterar sobre una lista en cada venta para encontrar el producto correspondiente.
- **Estructura resultante:**
  ```python
  { 'id_producto': { 'nombre': ..., 'precio': ..., 'stock_actual': ... } }
  ```

#### `leer_ventas()` -> Lista
- **Problema:** Las ventas deben de procesarse en el orden en que aparecen en el archivo `ventas.csv`, ya que una venta puede afectar de gran manera el stock disponible para la siguiente.
- **Solución:** Se optó mejor por una **lista** de diccionarios.
  - **Justificación:** Las listas en Python mantienen el orden de inserción de los elementos. Esto garantiza que el procesamiento se realice de forma secuencial, cumpliendo con las reglas de negocio y lo solicitado.
- **Estructura resultante:**
  ```python
  [ { 'id_producto': ..., 'cantidad': ... }, { ... } ]
  ```

### Implementación Técnica
- Se utiliza el módulo `csv` y específicamente `csv.DictReader` para leer los archivos. Esta elección facilita el acceso a los datos por nombre de columna (`fila['id_producto']`), haciendo el código más legible y menos propenso a errores que si se usaran índices numéricos.
- Se implementó manejo de excepciones (`try-except FileNotFoundError`) para controlar de mejor  forma los errores, evitando que en el caso en que los archivos de entrada no existan, evitando que el programa termine con un error no controlado.

---

## 2. Lógica Principal: `procesar_ventas()`

### Decisión de Diseño: Flujo de Control y Validación

El núcleo del sistema reside en esta función. Se diseñó un flujo de validación claro y secuencial dentro de un bucle que itera sobre la lista de ventas para procesar cada una de ellas.

1.  **Iteración Secuencial:** Se utiliza un bucle `for` para recorrer cada venta. El uso de `enumerate()` permite llevar un contador del número de venta para los reportes.

2.  **Validación de Existencia:**
    - `if id_prod not in productos:`
    - Esta es la primera y más rápida validación. Gracias a que `productos` es un diccionario, esta comprobación es extremadamente eficiente.

3.  **Validación de Stock:**
    - `if cantidad > productos[id_prod]['stock_actual']:`
    - Solo si el producto existe, se procede a verificar el stock.

4.  **Control de Flujo con `continue`:** Si una validación falla, se registra el error y se utiliza la sentencia `continue` para saltar inmediatamente a la siguiente iteración del bucle. Este enfoque es más limpio que anidar múltiples bloques `if-else`.

5.  **Actualización de Estado:** Para las ventas exitosas, el estado del sistema se modifica directamente: se decrementa el `stock_actual` en el diccionario de productos y se acumulan los `ingresos_totales`. Es importante destacar que el diccionario `productos` se modifica "por referencia", por lo que los cambios persisten fuera de la función.

### Retorno de Múltiples Valores
- La función retorna una tupla `(ventas_exitosas, ventas_fallidas, ingresos_totales)`. Esta decisión de diseño permite pasar todos los resultados del procesamiento a las funciones de generación de reportes de una sola vez, manteniendo el código organizado.

---

## 3. Generación de Reportes: `generar_inventario_actualizado()` y `generar_reporte_ventas()`

### `generar_inventario_actualizado()`
- **Tecnología:** Utiliza `csv.DictWriter` para escribir el archivo de salida. Esto asegura que los datos se escriban en las columnas correctas según el encabezado definido, lo que lo hace más robusto que la escritura manual.
- **Diseño:** La función recibe el diccionario de productos ya actualizado y simplemente lo "traduce" a un formato CSV, separando la lógica de procesamiento de la lógica de escritura.

### `generar_reporte_ventas()`
- **Análisis de Datos Adicional:** Esta función no solo escribe datos, sino que primero realiza cálculos adicionales para obtener métricas de negocio:
  1.  **Agrupación de Ventas:** Itera sobre las ventas exitosas para agruparlas por producto, sumando unidades e ingresos. Esto es un paso de pre-procesamiento necesario para los siguientes cálculos.
  2.  **Cálculo de Métricas:** Una vez agrupados los datos, se itera sobre ellos para encontrar el producto más vendido (por unidades) y el de mayores ingresos.
- **Formato de Salida:** Se utilizan f-strings de Python con especificadores de formato (`:,.2f`) para presentar los números de una manera legible para el usuario final (con separadores de miles y dos decimales).

---

## 4. Arquitectura General y `main()`

- **Función `main()` como Orquestador:** La función `main()` actúa como el punto de entrada que coordina la ejecución de todas las demás funciones en el orden correcto. Este diseño de "orquestador" hace que el flujo del programa sea muy fácil de seguir.
- **Modularidad:** Cada función tiene una responsabilidad única (leer productos, leer ventas, procesar, generar reporte). Este principio de diseño (Separación de incumbencias) hace que el código sea más fácil de mantener, depurar y extender en el futuro.
- **Punto de Entrada `if __name__ == "__main__":`:** Esta construcción estándar de Python asegura que el código dentro del bloque solo se ejecute cuando el archivo es el programa principal. Esto permite que, en el futuro, las funciones de este script puedan ser importadas por otros módulos (como `app.py`) sin que se ejecute automáticamente el proceso completo de la consola.
