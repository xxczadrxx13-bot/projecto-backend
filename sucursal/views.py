from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, F

from .models import Categoria, Producto, Cliente, Venta, DetalleVenta


# ==============================================================================
# 1. VISTA PÚBLICA · TIENDA Y CATÁLOGO DE INSTRUMENTOS (Acceso libre)
# ==============================================================================
def tienda_vitrina(request):
    """
    Catálogo público visible para clientes sin requerir inicio de sesión.
    Permite filtrar por categoría y buscar por nombre.
    """
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('q', '').strip()

    productos = Producto.objects.filter(activo=True).select_related('categoria')

    if categoria_id and categoria_id.isdigit():
        productos = productos.filter(categoria_id=int(categoria_id))
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    categorias = Categoria.objects.all().order_by('nombre')

    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_activa': int(categoria_id) if categoria_id and categoria_id.isdigit() else None,
        'busqueda': busqueda,
    }
    return render(request, "sucursal/vitrina.html", context)


# ==============================================================================
# 2. AUTENTICACIÓN SEGURA (Login / Logout mediante POST)
# ==============================================================================
def login_view(request):
    """
    Inicio de sesión seguro mediante formulario HTML puro y método POST.
    """
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        usuario = request.POST.get('username', '').strip()
        clave = request.POST.get('password', '').strip()

        user = authenticate(request, username=usuario, password=clave)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Bienvenido/a {user.username}.")
                next_url = request.GET.get('next')
                return redirect(next_url if next_url else 'admin_dashboard')
            else:
                messages.error(request, "Esta cuenta ha sido desactivada por un administrador.")
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")

    return render(request, 'sucursal/login.html')


def logout_view(request):
    """
    Cierre de sesión que exige petición POST para mitigar vulnerabilidades CSRF.
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, "Sesión cerrada correctamente.")
        return redirect('login')
    return redirect('admin_dashboard')


# ==============================================================================
# 3. DASHBOARD ADMINISTRATIVO
# ==============================================================================
@login_required
def admin_dashboard(request):
    """
    Panel de bienvenida y métricas clave de la sucursal.
    """
    total_productos = Producto.objects.filter(activo=True).count()
    total_clientes = Cliente.objects.count()
    total_ventas = Venta.objects.count()

    suma_ingresos = Venta.objects.aggregate(total_acumulado=Sum('total'))['total_acumulado'] or 0

    # Alerta de stock crítico (stock actual menor o igual al stock mínimo)
    stock_critico = Producto.objects.filter(stock__lte=F('stock_minimo'), activo=True)

    context = {
        'total_productos': total_productos,
        'total_clientes': total_clientes,
        'total_ventas': total_ventas,
        'ingresos_totales': suma_ingresos,
        'stock_critico': stock_critico,
    }
    return render(request, 'sucursal/dashboard.html', context)


# ==============================================================================
# 4. GESTIÓN DE PRODUCTOS (CRUD SIN MODELFORM)
# ==============================================================================
@login_required
def productos_lista(request):
    """
    Listado del catálogo administrativo con formulario integrado de creación rápida.
    """
    productos = Producto.objects.select_related('categoria').all().order_by('-id')
    categorias = Categoria.objects.all().order_by('nombre')

    return render(request, 'sucursal/productos_lista.html', {
        'productos': productos,
        'categorias': categorias,
    })


@login_required
def producto_crear(request):
    """
    Crea un producto capturando los datos desde la petición POST directa.
    """
    if request.method == 'POST':
        sku = request.POST.get('sku', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        categoria_id = request.POST.get('categoria', '').strip()
        precio_raw = request.POST.get('precio', '').strip()
        stock_raw = request.POST.get('stock', '').strip()
        stock_min_raw = request.POST.get('stock_minimo', '').strip()

        if not sku or not nombre or not categoria_id or not precio_raw:
            messages.error(request, "Todos los campos obligatorios deben ser completados.")
            return redirect('productos_lista')

        if Producto.objects.filter(sku=sku).exists():
            messages.error(request, f"Ya existe un producto registrado con el SKU '{sku}'.")
            return redirect('productos_lista')

        try:
            categoria_obj = Categoria.objects.get(id=categoria_id)
            precio = Decimal(precio_raw)
            stock = int(stock_raw) if stock_raw else 0
            stock_minimo = int(stock_min_raw) if stock_min_raw else 5

            if precio <= 0 or stock < 0 or stock_minimo < 0:
                messages.error(request, "Los valores numéricos de precio o stock no pueden ser negativos.")
                return redirect('productos_lista')

            Producto.objects.create(
                sku=sku,
                nombre=nombre,
                categoria=categoria_obj,
                precio=precio,
                stock=stock,
                stock_minimo=stock_minimo,
                activo=True
            )
            messages.success(request, f"Producto '{nombre}' creado exitosamente.")
        except Categoria.DoesNotExist:
            messages.error(request, "La categoría seleccionada no existe.")
        except (ValueError, Exception) as err:
            messages.error(request, f"Error al guardar producto: {err}")

    return redirect('productos_lista')


@login_required
def producto_editar(request, pk):
    """
    Edición de producto mediante formulario HTML con precarga manual de valores.
    """
    producto = get_object_or_404(Producto, pk=pk)
    categorias = Categoria.objects.all().order_by('nombre')

    if request.method == 'POST':
        sku = request.POST.get('sku', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        categoria_id = request.POST.get('categoria', '').strip()
        precio_raw = request.POST.get('precio', '').strip()
        stock_raw = request.POST.get('stock', '').strip()
        stock_min_raw = request.POST.get('stock_minimo', '').strip()
        activo = request.POST.get('activo') == 'on'

        if Producto.objects.filter(sku=sku).exclude(pk=producto.pk).exists():
            messages.error(request, f"El SKU '{sku}' ya pertenece a otro producto.")
            return render(request, 'sucursal/producto_editar.html', {
                'producto': producto,
                'categorias': categorias
            })

        try:
            producto.sku = sku
            producto.nombre = nombre
            producto.categoria = Categoria.objects.get(id=categoria_id)
            producto.precio = Decimal(precio_raw)
            producto.stock = int(stock_raw)
            producto.stock_minimo = int(stock_min_raw)
            producto.activo = activo
            producto.save()

            messages.success(request, f"Producto '{producto.nombre}' actualizado correctamente.")
            return redirect('productos_lista')
        except Exception as err:
            messages.error(request, f"Error en la actualización: {err}")

    return render(request, 'sucursal/producto_editar.html', {
        'producto': producto,
        'categorias': categorias
    })


@login_required
def producto_eliminar(request, pk):
    """
    Eliminación de producto protegida mediante petición POST.
    """
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"Producto '{nombre}' eliminado satisfactoriamente.")
    return redirect('productos_lista')


# ==============================================================================
# 5. GESTIÓN DE USUARIOS Y ROLES (Control de Superadministrador)
# ==============================================================================
@login_required
def usuarios_gestion(request):
    """
    Panel para crear usuarios capturando correo y asignando roles de sistema.
    """
    if not request.user.is_superuser:
        messages.error(request, "Acceso restringido: requiere permisos de Administrador.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        rol = request.POST.get('rol', 'vendedor')

        if not username or not password:
            messages.error(request, "El nombre de usuario y la contraseña son obligatorios.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, f"El usuario '{username}' ya existe.")
        else:
            nuevo_usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            if rol == 'administrador':
                nuevo_usuario.is_staff = True
            else:
                nuevo_usuario.is_staff = False
            nuevo_usuario.save()

            messages.success(request, f"Usuario '{username}' registrado correctamente.")
            return redirect('usuarios_gestion')

    usuarios = User.objects.all().order_by('id')
    return render(request, 'sucursal/usuarios_gestion.html', {'usuarios': usuarios})


@login_required
def usuario_toggle_estado(request, user_id):
    """
    Activa o desactiva lógicamente el acceso de un usuario.
    """
    if not request.user.is_superuser:
        messages.error(request, "No cuentas con permisos para alterar usuarios.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        if usuario == request.user:
            messages.error(request, "No puedes desactivar tu propia cuenta activa.")
        else:
            usuario.is_active = not usuario.is_active
            usuario.save()
            estado = "activado" if usuario.is_active else "desactivado"
            messages.success(request, f"El usuario '{usuario.username}' ha sido {estado}.")

    return redirect('usuarios_gestion')


# ==============================================================================
# 6. REPORTES Y AGREGACIONES ORM (Requerimiento Evaluación 3)
# ==============================================================================
@login_required
def reportes_view(request):
    """
    Generación de métricas de negocio con el ORM de Django (Group By y Sumatorias).
    """
    # 1. Ventas agrupadas por cliente (corregido a 'ventas' en plural)
    ventas_por_cliente = Cliente.objects.annotate(
        total_comprado=Sum('ventas__total'),
        cantidad_ventas=Count('ventas')
    ).filter(cantidad_ventas__gt=0).order_by('-total_comprado')

    # 2. Cantidad de productos y valor total del stock por categoría
    resumen_categorias = Categoria.objects.annotate(
        total_productos=Count('producto'),
        valor_inventario=Sum(F('producto__precio') * F('producto__stock'))
    ).order_by('nombre')

    # 3. Productos bajo stock mínimo
    productos_bajo_stock = Producto.objects.filter(
        stock__lte=F('stock_minimo'),
        activo=True
    ).select_related('categoria').order_by('stock')

    context = {
        'ventas_por_cliente': ventas_por_cliente,
        'resumen_categorias': resumen_categorias,
        'productos_bajo_stock': productos_bajo_stock,
    }
    return render(request, 'sucursal/reportes.html', context)