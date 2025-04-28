from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Estudiante
from .serializers import EstudianteSerializer

class BuscarEstudiantePorDni(APIView):
    def get(self, request, dni):
        try:
            estudiante = Estudiante.objects.get(dni=dni)
            serializer = EstudianteSerializer(estudiante)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Estudiante.DoesNotExist:
            return Response({"error": "Estudiante no encontrado"}, status=status.HTTP_404_NOT_FOUND)

class ActualizarFotoEstudiante(APIView):
    def post(self, request, dni):
        try:
            estudiante = Estudiante.objects.get(dni=dni)
            if 'foto' in request.FILES:
                estudiante.foto = request.FILES['foto']
                estudiante.save()
                return Response({"mensaje": "Foto actualizada correctamente"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No se envió ninguna foto"}, status=status.HTTP_400_BAD_REQUEST)
        except Estudiante.DoesNotExist:
            return Response({"error": "Estudiante no encontrado"}, status=status.HTTP_404_NOT_FOUND)


class RegistrarEstudiante(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        if not request.data:
            return Response({"error": "No se recibieron datos en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)
        
        nombres = request.data.get('nombres')
        apellido = request.data.get('apellido')
        tipodocumento = request.data.get('tipodocumento')
        dni = request.data.get('dni')
        

        # Validar que el DNI esté presente
        if not dni:
            return Response({"error": "El DNI es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el estudiante ya existe
        if Estudiante.objects.filter(dni=dni).exists():
            return Response({"error": "El estudiante ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear un nuevo estudiante
        estudiante = Estudiante(
            nombres=nombres,
            apellido=apellido,
            tipodocumento=tipodocumento,
            dni=dni,
            nombrecompleto=f"{apellido} {nombres}"
        )

        # Si hay una foto en la solicitud, la guardamos
        if 'foto' in request.FILES:
            estudiante.foto = request.FILES['foto']

        # Guardar el estudiante
        estudiante.save()

        # Serializar el estudiante guardado
        serializer = EstudianteSerializer(estudiante)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class BuscarEstudiantes(APIView):
    def get(self, request):
        # Obtener el parámetro 'apellido' de la consulta
        apellido_parcial = request.query_params.get('apellido', None)

        if not apellido_parcial:
            return Response({"error": "El parámetro 'apellido' es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        # Filtrar los estudiantes que coinciden con el apellido parcial
        estudiantes = Estudiante.objects.filter(apellido__icontains=apellido_parcial)

        # Si no se encuentran estudiantes, devolver un mensaje adecuado
        if not estudiantes.exists():
            return Response({"message": "No se encontraron estudiantes con ese apellido."}, status=status.HTTP_404_NOT_FOUND)

        # Serializar los datos de los estudiantes encontrados
        serializer = EstudianteSerializer(estudiantes, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    
class TestPostView(APIView):
    def post(self, request):
        # Solo devolver los datos recibidos
        print("Datos recibidos:", request.data)
        return Response({"message": "Solicitud POST exitosa", "data": request.data}, status=status.HTTP_200_OK)    
    
