from django.urls import path
from . import views

urlpatterns = [
    path('', views.vitrina_view, name='vitrina'),
    path('producto/<int:producto_id>/', views.detalle_producto_view, name='detalle_producto'),
    path('cotizador/', views.cotizador_view, name='cotizador'),
    path('administracion/', views.admin_productos_view, name='admin_productos'),
]