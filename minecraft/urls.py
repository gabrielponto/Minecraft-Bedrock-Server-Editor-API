from django.urls import path
from minecraft import views

urlpatterns = [
    path('', views.list_maps, name='minecraft_list_maps'),
    path('create_map/', views.create_map, name='minecraft_create_map'),
    path('change_map/', views.change_map, name='minecraft_change_map'),
    path('install_addon/', views.install_addon, name='minecraft_install_addon'),
    path('enable-behavior/', views.request_enable_behavior_pack, name='minecraft_enable_behavior_pack')
]
