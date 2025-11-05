"""
Servidor Web Flask para PyTech Store
Descripción: Provee una API REST para interactuar con el sistema de ventas
             y sirve la interfaz de usuario.
"""

from flask import Flask, jsonify, render_template
import csv

# Nombres de archivos (pueden ser configurables)
ARCHIVO_PRODUCTOS = 'productos.csv'
ARCHIVO_VENTAS = 'ventas.csv'
ARCHIVO_INVENTARIO_SALIDA = 'inventario_actualizado.csv'
ARCHIVO_REPORTE_SALIDA = 'reporte_ventas.txt'

app = Flask(__name__)

# --- Lógica de negocio adaptada (similar a sistema_ventas.py) ---

def leer_productos_base():
    """Lee los productos del CSV para obtener su estado inicial."""
    try:
        with open(ARCHIVO_PRODUCTOS, 'r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            productos = [
                {
                    'id': fila['id_producto'],
                    'nombre': fila['nombre_producto'],
                    'precio': float(fila['precio']),
                    'stock': int(fila['stock_inicial'])
                } for fila in lector
            ]
            return productos
    except FileNotFoundError:
        return []

def procesar_logica_ventas():
    """Ejecuta la lógica completa de procesamiento de ventas y retorna un resumen detallado."""
    # 1. Cargar datos
    try:
        with open(ARCHIVO_PRODUCTOS, 'r', encoding='utf-8') as f:
            productos = {p['id_producto']: {'nombre': p['nombre_producto'], 'precio': float(p['precio']), 'stock_inicial': int(p['stock_inicial']), 'stock_actual': int(p['stock_inicial'])} for p in csv.DictReader(f)}
        with open(ARCHIVO_VENTAS, 'r', encoding='utf-8') as f:
            ventas = [{'id_producto': v['id_producto'], 'cantidad': int(v['cantidad'])} for v in csv.DictReader(f)]
    except FileNotFoundError as e:
        return {'error': f"No se encontró el archivo: {e.filename}"}
    except Exception as e:
        return {'error': f"Error al leer archivos CSV: {e}"}

    # 2. Procesar ventas
    ventas_exitosas_detalles = []
    ventas_fallidas_detalles = []
    ingresos_totales = 0.0

    for i, venta in enumerate(ventas, 1):
        id_prod = venta['id_producto']
        cantidad = venta['cantidad']
        
        if id_prod not in productos:
            ventas_fallidas_detalles.append({
                'numero': i, 'id_producto': id_prod, 'razon': 'Producto no existe',
                'mensaje': f"Producto '{id_prod}' no existe en el catálogo."
            })
            continue

        stock_disponible = productos[id_prod]['stock_actual']
        if cantidad > stock_disponible:
            ventas_fallidas_detalles.append({
                'numero': i, 'id_producto': id_prod, 'razon': 'Stock insuficiente',
                'mensaje': f"Solicitado: {cantidad}, Disponible: {stock_disponible}"
            })
            continue

        precio_unitario = productos[id_prod]['precio']
        ingreso_venta = precio_unitario * cantidad
        productos[id_prod]['stock_actual'] -= cantidad
        ingresos_totales += ingreso_venta

        ventas_exitosas_detalles.append({
            'numero': i, 'id_producto': id_prod, 'nombre': productos[id_prod]['nombre'],
            'cantidad': cantidad, 'precio_unitario': precio_unitario, 'ingreso': ingreso_venta,
            'stock_restante': productos[id_prod]['stock_actual']
        })

    # 3. Generar datos para reportes
    ventas_por_producto = {}
    for v in ventas_exitosas_detalles:
        pid = v['id_producto']
        if pid not in ventas_por_producto:
            ventas_por_producto[pid] = {'nombre': v['nombre'], 'unidades': 0, 'ingresos': 0.0}
        ventas_por_producto[pid]['unidades'] += v['cantidad']
        ventas_por_producto[pid]['ingresos'] += v['ingreso']

    producto_mas_vendido = max(ventas_por_producto.values(), key=lambda x: x['unidades'], default=None)
    producto_mayores_ingresos = max(ventas_por_producto.values(), key=lambda x: x['ingresos'], default=None)

    # 4. Generar inventario actualizado
    inventario_actualizado = []
    for id_prod, datos in productos.items():
        vendido = datos['stock_inicial'] - datos['stock_actual']
        inventario_actualizado.append({
            'id': id_prod, 'nombre': datos['nombre'], 'precio': datos['precio'],
            'stock_inicial': datos['stock_inicial'], 'vendido': vendido, 'stock_final': datos['stock_actual']
        })

    # 5. Generar archivos de salida (sobrescribir)
    try:
        # Inventario CSV
        with open(ARCHIVO_INVENTARIO_SALIDA, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'nombre', 'precio', 'stock_inicial', 'vendido', 'stock_final'])
            writer.writeheader()
            writer.writerows(inventario_actualizado)
        # Reporte TXT
        with open(ARCHIVO_REPORTE_SALIDA, 'w', encoding='utf-8') as f:
            f.write("=== Reporte de Ventas PyTech Store ===\n\n")
            f.write(f"Ingresos Totales: ${ingresos_totales:,.2f}\n\n")
            if producto_mas_vendido:
                f.write(f"Producto Más Vendido (unidades): '{producto_mas_vendido['nombre']}', con {producto_mas_vendido['unidades']} unidades.\n")
            if producto_mayores_ingresos:
                f.write(f"Producto con Mayores Ingresos: '{producto_mayores_ingresos['nombre']}', generando ${producto_mayores_ingresos['ingresos']:,.2f}.\n")
            f.write("\n--- Ventas No Procesadas ---\n")
            if ventas_fallidas_detalles:
                for v in ventas_fallidas_detalles:
                    f.write(f"- {v['razon']} para '{v['id_producto']}': {v['mensaje']}\n")
            else:
                f.write("- No hay ventas rechazadas.\n")
    except Exception as e:
        return {'error': f"Error al escribir archivos de salida: {e}"}

    # 6. Preparar respuesta JSON
    return {
        'ingresos_totales': ingresos_totales,
        'total_ventas_exitosas': len(ventas_exitosas_detalles),
        'total_ventas_fallidas': len(ventas_fallidas_detalles),
        'ventas_exitosas': ventas_exitosas_detalles,
        'ventas_fallidas': ventas_fallidas_detalles,
        'producto_mas_vendido': producto_mas_vendido,
        'producto_mayores_ingresos': producto_mayores_ingresos,
        'inventario_actualizado': inventario_actualizado,
        'ventas_por_producto': list(ventas_por_producto.values())
    }

# --- Rutas de la API ---

@app.route('/')
def index():
    """Sirve la página principal."""
    return render_template('index.html')

@app.route('/api/productos')
def get_productos():
    """Retorna el catálogo de productos inicial."""
    productos = leer_productos_base()
    return jsonify(productos)

@app.route('/api/procesar')
def procesar_ventas_api():
    """Endpoint para procesar las ventas y retornar los resultados."""
    resultado = procesar_logica_ventas()
    if 'error' in resultado:
        return jsonify(resultado), 500
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True, port=5000)