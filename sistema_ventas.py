"""
Sistema de Gestión de Inventario y Ventas - PyTech Store
Autor: Desarrollado para el curso de Algoritmos y Programación
Descripción: Este programa procesa ventas y actualiza el inventario de una tienda de tecnología
"""

import csv


def leer_productos(archivo_productos):
    """
    Lee el archivo de productos y retorna un diccionario con la información.
    
    Args:
        archivo_productos (str): Ruta del archivo productos.csv
    
    Returns:
        dict: Diccionario donde la clave es el id_producto y el valor es otro diccionario
              con nombre, precio, stock_inicial y stock_actual
    """
    productos = {}
    
    try:
        with open(archivo_productos, 'r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            
            for fila in lector:
                id_prod = fila['id_producto']
                productos[id_prod] = {
                    'nombre': fila['nombre_producto'],
                    'precio': float(fila['precio']),
                    'stock_inicial': int(fila['stock_inicial']),
                    'stock_actual': int(fila['stock_inicial'])  # Al inicio, stock_actual = stock_inicial
                }
        
        print(f"✓ Se cargaron {len(productos)} productos correctamente.")
        return productos
    
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{archivo_productos}'")
        return None
    except Exception as e:
        print(f"❌ Error al leer productos: {e}")
        return None


def leer_ventas(archivo_ventas):
    """
    Lee el archivo de ventas y retorna una lista con las solicitudes de compra.
    
    Args:
        archivo_ventas (str): Ruta del archivo ventas.csv
    
    Returns:
        list: Lista de diccionarios con id_producto y cantidad
    """
    ventas = []
    
    try:
        with open(archivo_ventas, 'r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            
            for fila in lector:
                ventas.append({
                    'id_producto': fila['id_producto'],
                    'cantidad': int(fila['cantidad'])
                })
        
        print(f"✓ Se cargaron {len(ventas)} solicitudes de venta.")
        return ventas
    
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{archivo_ventas}'")
        return None
    except Exception as e:
        print(f"❌ Error al leer ventas: {e}")
        return None


def procesar_ventas(productos, ventas):
    """
    Procesa todas las ventas según las reglas de negocio.
    
    Reglas:
    1. El producto debe existir en el catálogo
    2. Debe haber suficiente stock disponible
    3. Las ventas se procesan en orden
    
    Args:
        productos (dict): Diccionario de productos
        ventas (list): Lista de solicitudes de venta
    
    Returns:
        tuple: (ventas_exitosas, ventas_fallidas, ingresos_totales)
    """
    ventas_exitosas = []
    ventas_fallidas = []
    ingresos_totales = 0.0
    
    print("\n" + "="*60)
    print("PROCESANDO VENTAS...")
    print("="*60)
    
    for i, venta in enumerate(ventas, 1):
        id_prod = venta['id_producto']
        cantidad = venta['cantidad']
        
        print(f"\nVenta #{i}: {id_prod} - {cantidad} unidades")
        
        # Regla 1: Verificar si el producto existe
        if id_prod not in productos:
            mensaje_error = f"Producto '{id_prod}' no existe en el catálogo. Cantidad solicitada: {cantidad}"
            ventas_fallidas.append(mensaje_error)
            print(f"  ❌ RECHAZADA: Producto no existe")
            continue
        
        # Regla 2: Verificar si hay suficiente stock
        stock_disponible = productos[id_prod]['stock_actual']
        
        if cantidad > stock_disponible:
            mensaje_error = f"Stock insuficiente para '{productos[id_prod]['nombre']}' ({id_prod}). Solicitado: {cantidad}, Disponible: {stock_disponible}"
            ventas_fallidas.append(mensaje_error)
            print(f"  ❌ RECHAZADA: Stock insuficiente (Disponible: {stock_disponible})")
            continue
        
        # Venta exitosa: actualizar stock y calcular ingresos
        productos[id_prod]['stock_actual'] -= cantidad
        ingreso_venta = productos[id_prod]['precio'] * cantidad
        ingresos_totales += ingreso_venta
        
        ventas_exitosas.append({
            'id_producto': id_prod,
            'nombre': productos[id_prod]['nombre'],
            'cantidad': cantidad,
            'ingreso': ingreso_venta
        })
        
        print(f"  ✓ APROBADA: ${ingreso_venta:.2f} - Stock restante: {productos[id_prod]['stock_actual']}")
    
    print("\n" + "="*60)
    print(f"RESUMEN: {len(ventas_exitosas)} ventas exitosas, {len(ventas_fallidas)} rechazadas")
    print("="*60)
    
    return ventas_exitosas, ventas_fallidas, ingresos_totales


def generar_inventario_actualizado(productos, archivo_salida):
    """
    Genera el archivo CSV con el inventario actualizado.
    
    Args:
        productos (dict): Diccionario de productos con stock actualizado
        archivo_salida (str): Nombre del archivo de salida
    """
    try:
        with open(archivo_salida, 'w', newline='', encoding='utf-8') as archivo:
            campos = ['id_producto', 'nombre_producto', 'precio', 'stock_inicial', 'stock_final']
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            
            escritor.writeheader()
            
            for id_prod, datos in productos.items():
                escritor.writerow({
                    'id_producto': id_prod,
                    'nombre_producto': datos['nombre'],
                    'precio': datos['precio'],
                    'stock_inicial': datos['stock_inicial'],
                    'stock_final': datos['stock_actual']
                })
        
        print(f"\n✓ Inventario actualizado guardado en '{archivo_salida}'")
        return True
    
    except Exception as e:
        print(f"\n❌ Error al generar inventario: {e}")
        return False


def generar_reporte_ventas(ventas_exitosas, ventas_fallidas, ingresos_totales, archivo_salida):
    """
    Genera el reporte de ventas en formato texto.
    
    Args:
        ventas_exitosas (list): Lista de ventas procesadas exitosamente
        ventas_fallidas (list): Lista de mensajes de error de ventas fallidas
        ingresos_totales (float): Total de ingresos generados
        archivo_salida (str): Nombre del archivo de salida
    """
    try:
        # Calcular producto más vendido (por unidades)
        producto_mas_vendido = None
        max_unidades = 0
        ventas_por_producto = {}
        
        for venta in ventas_exitosas:
            id_prod = venta['id_producto']
            if id_prod not in ventas_por_producto:
                ventas_por_producto[id_prod] = {
                    'nombre': venta['nombre'],
                    'unidades': 0,
                    'ingresos': 0.0
                }
            ventas_por_producto[id_prod]['unidades'] += venta['cantidad']
            ventas_por_producto[id_prod]['ingresos'] += venta['ingreso']
        
        # Encontrar producto más vendido por unidades
        for id_prod, datos in ventas_por_producto.items():
            if datos['unidades'] > max_unidades:
                max_unidades = datos['unidades']
                producto_mas_vendido = (id_prod, datos['nombre'], datos['unidades'])
        
        # Encontrar producto con mayores ingresos
        producto_mayores_ingresos = None
        max_ingresos = 0.0
        
        for id_prod, datos in ventas_por_producto.items():
            if datos['ingresos'] > max_ingresos:
                max_ingresos = datos['ingresos']
                producto_mayores_ingresos = (id_prod, datos['nombre'], datos['ingresos'])
        
        # Escribir el reporte
        with open(archivo_salida, 'w', encoding='utf-8') as archivo:
            archivo.write("=== Reporte de Ventas PyTech Store ===\n\n")
            archivo.write(f"Ingresos Totales: ${ingresos_totales:,.2f}\n\n")
            
            if producto_mas_vendido:
                archivo.write(f"Producto Más Vendido (unidades): '{producto_mas_vendido[1]}' ({producto_mas_vendido[0]}), con {producto_mas_vendido[2]} unidades.\n")
            else:
                archivo.write("Producto Más Vendido (unidades): No hay ventas registradas.\n")
            
            if producto_mayores_ingresos:
                archivo.write(f"Producto con Mayores Ingresos: '{producto_mayores_ingresos[1]}' ({producto_mayores_ingresos[0]}), generando ${producto_mayores_ingresos[2]:,.2f}.\n")
            else:
                archivo.write("Producto con Mayores Ingresos: No hay ventas registradas.\n")
            
            archivo.write("\n--- Ventas No Procesadas ---\n")
            
            if ventas_fallidas:
                for error in ventas_fallidas:
                    archivo.write(f"- {error}\n")
            else:
                archivo.write("- No hay ventas rechazadas. ¡Todas las ventas fueron exitosas!\n")
        
        print(f"✓ Reporte de ventas guardado en '{archivo_salida}'")
        return True
    
    except Exception as e:
        print(f"❌ Error al generar reporte: {e}")
        return False


def main():
    """
    Función principal que coordina todo el proceso.
    """
    print("\n" + "="*60)
    print("  SISTEMA DE GESTIÓN DE INVENTARIO Y VENTAS")
    print("  PyTech Store")
    print("="*60 + "\n")
    
    # Nombres de los archivos
    archivo_productos = 'productos.csv'
    archivo_ventas = 'ventas.csv'
    archivo_inventario_salida = 'inventario_actualizado.csv'
    archivo_reporte_salida = 'reporte_ventas.txt'
    
    # Paso 1: Leer productos
    print("PASO 1: Cargando catálogo de productos...")
    productos = leer_productos(archivo_productos)
    if productos is None:
        return
    
    # Paso 2: Leer ventas
    print("\nPASO 2: Cargando solicitudes de venta...")
    ventas = leer_ventas(archivo_ventas)
    if ventas is None:
        return
    
    # Paso 3: Procesar ventas
    print("\nPASO 3: Procesando ventas según reglas de negocio...")
    ventas_exitosas, ventas_fallidas, ingresos_totales = procesar_ventas(productos, ventas)
    
    # Paso 4: Generar inventario actualizado
    print("\nPASO 4: Generando inventario actualizado...")
    generar_inventario_actualizado(productos, archivo_inventario_salida)
    
    # Paso 5: Generar reporte de ventas
    print("\nPASO 5: Generando reporte de ventas...")
    generar_reporte_ventas(ventas_exitosas, ventas_fallidas, ingresos_totales, archivo_reporte_salida)
    
    # Resumen final
    print("\n" + "="*60)
    print("  PROCESO COMPLETADO EXITOSAMENTE")
    print("="*60)
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   • Ingresos totales: ${ingresos_totales:,.2f}")
    print(f"   • Ventas exitosas: {len(ventas_exitosas)}")
    print(f"   • Ventas rechazadas: {len(ventas_fallidas)}")
    print(f"\n📁 ARCHIVOS GENERADOS:")
    print(f"   • {archivo_inventario_salida}")
    print(f"   • {archivo_reporte_salida}")
    print("\n" + "="*60 + "\n")


# Punto de entrada del programa
if __name__ == "__main__":
    main()
