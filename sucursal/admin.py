from django.contrib import admin
from .models import Categoria, Producto

admin.site.site_header = "Music Pro S.A. - Administración de Sucursal"
admin.site.site_title = "Music Pro Admin"
admin.site.index_title = "Panel de Control y Punto de Venta"

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'total_productos')
    search_fields = ('nombre',)
    ordering = ('nombre',)

    def total_productos(self, obj):
        return obj.productos.count()
    total_productos.short_description = "N° de Productos"


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio_formateado', 'stock', 'activo', 'fecha_creacion')
    list_filter = ('categoria', 'activo', 'fecha_creacion')
    search_fields = ('codigo', 'nombre', 'descripcion')
    list_editable = ('stock', 'activo')
    list_per_page = 25
    ordering = ('-fecha_creacion',)
    
    actions = ['marcar_como_activos', 'marcar_como_inactivos']

    def precio_formateado(self, obj):
        return f"${obj.precio:,} CLP".replace(",", ".")
    precio_formateado.short_description = "Precio"

    @admin.action(description="Activar productos seleccionados")
    def marcar_como_activos(self, request, queryset):
        filas_actualizadas = queryset.update(activo=True)
        self.message_user(request, f"{filas_actualizadas} productos fueron activados exitosamente.")

    @admin.action(description="Desactivar productos seleccionados")
    def marcar_como_inactivos(self, request, queryset):
        filas_actualizadas = queryset.update(activo=False)
        self.message_user(request, f"{filas_actualizadas} productos fueron desactivados.")