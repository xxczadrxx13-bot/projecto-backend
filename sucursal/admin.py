from django.contrib import admin
from .models import Categoria, Producto, Cliente, Venta, DetalleVenta


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'categoria', 'precio', 'stock', 'stock_minimo', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('sku', 'nombre')
    list_editable = ('precio', 'stock', 'activo')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'email', 'telefono')
    search_fields = ('rut', 'nombre')


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'vendedor', 'total', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('cliente__nombre', 'cliente__rut')
    inlines = [DetalleVentaInline]