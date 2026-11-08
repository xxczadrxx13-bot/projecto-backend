from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.tienda_vitrina, name='vitrina'),
    path('tienda/', views.tienda_vitrina, name='vitrina_catalogo'),

  
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),


    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/productos/', views.productos_lista, name='productos_lista'),
    path('admin-panel/productos/crear/', views.producto_crear, name='producto_crear'),
    path('admin-panel/productos/editar/<int:pk>/', views.producto_editar, name='producto_editar'),
    path('admin-panel/productos/eliminar/<int:pk>/', views.producto_eliminar, name='producto_eliminar'),
    path('admin-panel/usuarios/', views.usuarios_gestion, name='usuarios_gestion'),
    path('admin-panel/usuarios/toggle/<int:user_id>/', views.usuario_toggle_estado, name='usuario_toggle_estado'),
    path('admin-panel/reportes/', views.reportes_view, name='reportes'),
]