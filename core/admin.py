from django.contrib import admin
from .models import Estudiante,Secciones,Grados,Tutores,Profesores,Apoderados,Mensajes,Asistencia

admin.site.register([Estudiante,Secciones,Grados,Tutores,Profesores,Apoderados,Mensajes,Asistencia])
