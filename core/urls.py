from django.urls import path
from .views import BuscarEstudiantePorDni, ActualizarFotoEstudiante,RegistrarEstudiante,TestPostView,BuscarEstudiantes,index,Alumnos_listado,actualizar_data_secciones,Editar_alumnos,generar_carnet_pdf

urlpatterns = [
    path('estudiante/<str:dni>/', BuscarEstudiantePorDni.as_view(), name='buscar_estudiante'),
    path('estudiante/<str:dni>/foto/', ActualizarFotoEstudiante.as_view(), name='actualizar_foto_estudiante'),
    path('registrar/', RegistrarEstudiante.as_view(), name='registrar_estudiante'),
    path('buscar/', BuscarEstudiantes.as_view(), name='buscar_estudiante'),
    path('test-post/', TestPostView.as_view(), name='test_post'),
    path('index_home/', index,name="index_home"),
    path('listado_alumnos/', Alumnos_listado,name="listado_alumnos"),
    path('actualizar-data/', actualizar_data_secciones, name='actualizar_data_secciones'),
    path('Editar_alumnos/<str:id>/', Editar_alumnos, name='Editar_alumnos'),
    path('alumno/<int:alumno_id>/carnet/', generar_carnet_pdf, name='generar_carnet'),
]


#http://127.0.0.1:8000/api/registrar/
#http://127.0.0.1:8000/api/buscar/?apellido=RUIZ