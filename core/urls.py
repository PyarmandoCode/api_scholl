from django.urls import path
from .views import BuscarEstudiantePorDni, ActualizarFotoEstudiante,RegistrarEstudiante,TestPostView,BuscarEstudiantes

urlpatterns = [
    path('estudiante/<str:dni>/', BuscarEstudiantePorDni.as_view(), name='buscar_estudiante'),
    path('estudiante/<str:dni>/foto/', ActualizarFotoEstudiante.as_view(), name='actualizar_foto_estudiante'),
    path('registrar/', RegistrarEstudiante.as_view(), name='registrar_estudiante'),
    path('buscar/', BuscarEstudiantes.as_view(), name='buscar_estudiante'),
    path('test-post/', TestPostView.as_view(), name='test_post'),
]

#http://127.0.0.1:8000/api/registrar/
#http://127.0.0.1:8000/api/buscar/?apellido=RUIZ