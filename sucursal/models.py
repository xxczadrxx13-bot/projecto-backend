from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    codigo = models.CharField(max_length=30, unique=True, verbose_name="Código SKU")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos", verbose_name="Categoría")
    precio = models.PositiveIntegerField(verbose_name="Precio CLP")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock en Sucursal")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción Técnica")
    imagen = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL de Imagen")
    activo = models.BooleanField(default=True, verbose_name="Disponible para Venta")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"