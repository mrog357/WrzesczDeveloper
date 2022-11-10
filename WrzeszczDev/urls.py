from django.urls import path

from . import views

urlpatterns = [

    path('', views.map, name='map'),

    path('add_code/', views.add_code, name='add_code'),

    path ('<int:plot_id>/', views.plot, name='plot'),

    path ('<int:plot_id>/build/<int:build_id>', views.build, name='build'),

    path ('<int:plot_id>/building/<str:building_name>', views.building, name='building'),

    path('ranking/', views.ranking, name='ranking'),

    path('zoom/<int:zoom>', views.zoom_map, name='zoom_map'),

    path('adminex', views.adminex, name='adminex'),

    path('adminex/map/<int:zoom>', views.adminex_map, name='adminex_map'),

    path('adminex/plot/<int:plot_id>', views.adminex_plot, name='adminex_plot'),
    path('adminex/<int:plot_id>/build/<str:building_name>', views.adminex_build, name='adminex_build'),
    path('adminex/update', views.adminex_update_all, name='adminex_update_all'),
    path('adminex/add_csv', views.adminex_add_csv, name='adminex_update_all')



]
