from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Categoria, Producto

def vitrina_view(request):
    productos = Producto.objects.filter(activo=True)
    categoria_id = request.GET.get('categoria', '').strip()
    busqueda = request.GET.get('q', '').strip()

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | Q(codigo__icontains=busqueda)
        )

    categorias = Categoria.objects.all()

    context = {
        'productos': productos[:60], # Paginación visual inicial
        'categorias': categorias,
        'categoria_seleccionada': int(categoria_id) if categoria_id.isdigit() else None,
        'busqueda': busqueda,
    }
    return render(request, 'sucursal/vitrina.html', context)

def detalle_producto_view(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'sucursal/detalle_producto.html', {'producto': producto})

def cotizador_view(request):
    productos = Producto.objects.filter(activo=True, stock__gt=0)[:100]
    cotizacion = None

    if request.method == 'POST':
        try:
            prod_id = int(request.POST.get('producto_id', 0))
            cantidad = int(request.POST.get('cantidad', 1))
            es_club = request.POST.get('club_socio') == 'on'

            producto = Producto.objects.filter(id=prod_id).first()

            if producto and cantidad > 0:
                subtotal = producto.precio * cantidad
                descuento = int(subtotal * 0.10) if es_club else 0
                neto = subtotal - descuento
                iva = int(neto * 0.19)
                total = neto + iva

                cotizacion = {
                    'producto': producto.nombre,
                    'codigo': producto.codigo,
                    'precio_unitario': producto.precio,
                    'cantidad': cantidad,
                    'subtotal': subtotal,
                    'descuento': descuento,
                    'iva': iva,
                    'total': total,
                    'socio': es_club
                }
                messages.success(request, "Cotización generada exitosamente desde la Base de Datos.")
            else:
                messages.error(request, "Seleccione un producto disponible.")
        except (ValueError, TypeError):
            messages.error(request, "Datos numéricos no válidos.")

    return render(request, 'sucursal/cotizador.html', {'productos': productos, 'cotizacion': cotizacion})

def admin_productos_view(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.select_related('categoria').all()[:50]

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        codigo = request.POST.get('codigo', '').strip().upper()
        categoria_id = request.POST.get('categoria_id')
        precio_str = request.POST.get('precio', '0')
        stock_str = request.POST.get('stock', '0')
        imagen = request.POST.get('imagen', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if not nombre or not codigo or not categoria_id:
            messages.error(request, "Todos los campos obligatorios deben ser completados.")
        else:
            try:
                categoria = Categoria.objects.get(id=categoria_id)
                Producto.objects.create(
                    codigo=codigo,
                    nombre=nombre,
                    categoria=categoria,
                    precio=int(precio_str),
                    stock=int(stock_str),
                    imagen=imagen or "https://via.placeholder.com/400x300?text=Music+Pro",
                    descripcion=descripcion
                )
                messages.success(request, f"Producto {nombre} guardado en la Base de Datos.")
                return redirect('admin_productos')
            except Exception as e:
                messages.error(request, f"Error al guardar: {e}")

    return render(request, 'sucursal/admin_productos.html', {'productos': productos, 'categorias': categorias})