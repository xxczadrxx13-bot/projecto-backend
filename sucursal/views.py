import json
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

DATA_FILE = os.path.join(settings.BASE_DIR, 'sucursal', 'data', 'productos.json')

def cargar_productos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_productos(lista):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)

def vitrina_view(request):
    productos = cargar_productos()
    categoria_filtro = request.GET.get('categoria', '').strip()
    busqueda = request.GET.get('q', '').strip().lower()

    if categoria_filtro:
        productos = [p for p in productos if p.get('categoria') == categoria_filtro]

    if busqueda:
        productos = [p for p in productos if busqueda in p.get('nombre', '').lower() or busqueda in p.get('codigo', '').lower()]

    categorias = sorted(list(set([p.get('categoria') for p in cargar_productos() if p.get('categoria')])))

    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_filtro,
        'busqueda': busqueda,
    }
    return render(request, 'sucursal/vitrina.html', context)

def detalle_producto_view(request, producto_id):
    productos = cargar_productos()
    producto = next((p for p in productos if p.get('id') == producto_id), None)

    if not producto:
        messages.error(request, "El producto seleccionado no existe.")
        return redirect('vitrina')

    return render(request, 'sucursal/detalle_producto.html', {'producto': producto})

def cotizador_view(request):
    productos = cargar_productos()
    cotizacion = None

    if request.method == 'POST':
        try:
            prod_id = int(request.POST.get('producto_id', 0))
            cantidad = int(request.POST.get('cantidad', 1))
            es_club = request.POST.get('club_socio') == 'on'

            producto = next((p for p in productos if p.get('id') == prod_id), None)

            if producto and cantidad > 0:
                subtotal = producto['precio'] * cantidad
                descuento = int(subtotal * 0.10) if es_club else 0
                neto = subtotal - descuento
                iva = int(neto * 0.19)
                total = neto + iva

                cotizacion = {
                    'producto': producto['nombre'],
                    'codigo': producto['codigo'],
                    'precio_unitario': producto['precio'],
                    'cantidad': cantidad,
                    'subtotal': subtotal,
                    'descuento': descuento,
                    'iva': iva,
                    'total': total,
                    'socio': es_club
                }
                messages.success(request, "Cotización generada exitosamente.")
            else:
                messages.error(request, "Seleccione un producto y una cantidad válida.")
        except ValueError:
            messages.error(request, "Formato numérico no válido.")

    return render(request, 'sucursal/cotizador.html', {'productos': productos, 'cotizacion': cotizacion})

def admin_productos_view(request):
    productos = cargar_productos()

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        codigo = request.POST.get('codigo', '').strip().upper()
        categoria = request.POST.get('categoria', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        precio_str = request.POST.get('precio', '0')
        stock_str = request.POST.get('stock', '0')
        imagen = request.POST.get('imagen', '').strip()

        if not nombre or not codigo or not categoria:
            messages.error(request, "Todos los campos principales son obligatorios.")
        else:
            try:
                nuevo_id = max([p['id'] for p in productos], default=0) + 1
                nuevo = {
                    "id": nuevo_id,
                    "codigo": codigo,
                    "nombre": nombre,
                    "categoria": categoria,
                    "descripcion": descripcion or "Sin descripción.",
                    "precio": int(precio_str),
                    "stock": int(stock_str),
                    "imagen": imagen or "https://via.placeholder.com/400x300?text=Music+Pro"
                }
                productos.append(nuevo)
                guardar_productos(productos)
                messages.success(request, f"Producto {nombre} agregado con éxito al catálogo JSON.")
                return redirect('admin_productos')
            except ValueError:
                messages.error(request, "Precio y Stock deben ser números enteros.")

    return render(request, 'sucursal/admin_productos.html', {'productos': productos})