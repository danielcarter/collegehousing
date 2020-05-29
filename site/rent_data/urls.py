from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('reports/', views.reports, name='reports'),
    path('about/', views.about, name='about'),
    path('process/', views.process, name='process'),

    path('properties', views.properties, name='properties'),

    path('analysis', views.analysis, name='analysis'),

    path('export_properties', views.export_properties, name='export_properties'),

    path('export_fire_reports', views.export_fire_reports, name='export_fire_reports'),

    path('export_police_reports', views.export_police_reports, name='export_police_reports'),

    path('property/<int:id>', views.property, name='property'),

    path('owners/', views.owners, name='owners'),

    path('owner/<int:id>', views.owner, name='owner')

]
