from django.shortcuts import  render,redirect,get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Estudiante,Grados,Secciones
from .serializers import EstudianteSerializer
import pandas as pd
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.http import FileResponse
from reportlab.lib.pagesizes import portrait
import barcode

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
    


"""
Esta es la Parte del Frontend
"""
def index(request):
    template_name="Index.html"
    return render(request,template_name)

def Alumnos_listado(request):
    alumnos = Estudiante.objects.all()
    context = {
        "alumnos": alumnos,
    }
    template_name = "Listado_alumnos.html"
    return render(request, template_name, context) 

def actualizar_data_secciones(request):
    template_name="Listado_alumnos.html"
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        try:
            df = pd.read_excel(archivo)
            actualizados = 0
            no_encontrados = []

            for index, fila in df.iterrows():
                dni = str(fila[3]).strip()
                nombre_grado = str(fila[1]).strip()
                nombre_aula = str(fila[2]).strip()

                try:
                    alumno = Estudiante.objects.get(dni=dni)
                    grado = Grados.objects.filter(Grado__iexact=nombre_grado).first()
                    aula = Secciones.objects.filter(Seccion__iexact=nombre_aula).first()

                    if grado and aula:
                        alumno.grado = grado
                        alumno.aula = aula
                        alumno.save()
                        actualizados += 1
                    else:
                        no_encontrados.append(dni)
                except Estudiante.DoesNotExist:
                    no_encontrados.append(dni)

            messages.success(request, f'{actualizados} alumnos actualizados.')
            if no_encontrados:
                messages.warning(request, f'DNIs no encontrados o grado/aula inválidos: {", ".join(no_encontrados[:10])}...')
        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {e}')

        return redirect('actualizar_data_secciones')

    return render(request, template_name)

def Editar_alumnos(request,id):
    alumno=Estudiante.objects.get(id=id)
    grados = Grados.objects.all()
    secciones=Secciones.objects.all()
    context = {
        "grados": grados,
        "secciones": secciones,
        "alumno":alumno
    }
    template_name="Editar_alumnos.html"
    return render(request,template_name,context)

def generar_carnet_pdf(request, alumno_id):
    alumno = Estudiante.objects.get(id=alumno_id)

    # Tamaño vertical del carné: 54 mm x 85.6 mm
    CARD_WIDTH = 54 * mm
    CARD_HEIGHT = 85.6 * mm
    carnet = canvas.Canvas(BytesIO(), pagesize=(CARD_WIDTH, CARD_HEIGHT))

    # Fondo claro
    carnet.setFillColorRGB(0.95, 0.95, 0.95)
    carnet.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1)

    # Borde externo rojo (más grueso)
    margen_rojo = 1 * mm
    carnet.setStrokeColorRGB(1, 0, 0)  # rojo
    carnet.setLineWidth(3)
    carnet.rect(
        margen_rojo,
        margen_rojo,
        CARD_WIDTH - 2 * margen_rojo,
        CARD_HEIGHT - 2 * margen_rojo,
        fill=0,
        stroke=1
    )

    # Borde interno azul
    margen_azul = 3.5 * mm
    carnet.setStrokeColorRGB(0, 0, 1)  # azul
    carnet.setLineWidth(2)
    carnet.rect(
        margen_azul,
        margen_azul,
        CARD_WIDTH - 2 * margen_azul,
        CARD_HEIGHT - 2 * margen_azul,
        fill=0,
        stroke=1
    )

    center_x = CARD_WIDTH / 2

    # Foto centrada
    if alumno.foto:
        foto_path = alumno.foto.path
        foto_width = 30 * mm
        foto_height = 30 * mm
        carnet.drawImage(
            foto_path,
            center_x - foto_width / 2,
            CARD_HEIGHT - foto_height - 10 * mm,
            width=foto_width,
            height=foto_height
        )

    # Texto centrado en negro
    carnet.setFillColorRGB(0, 0, 0)
    carnet.setFont("Helvetica-Bold", 7.5)
    carnet.drawCentredString(center_x, CARD_HEIGHT - 45 * mm, f"{alumno.nombres} {alumno.apellido}")
    carnet.drawCentredString(center_x, CARD_HEIGHT - 49 * mm, f"DNI: {alumno.dni}")
    carnet.drawCentredString(center_x, CARD_HEIGHT - 53 * mm, f"Grado: {alumno.grado}")
    carnet.drawCentredString(center_x, CARD_HEIGHT - 57 * mm, f"Aula: {alumno.aula}")

    # Código de barras centrado
    barcode_class = barcode.get_barcode_class('code128')
    codigo = barcode_class(str(alumno.dni), writer=ImageWriter())
    barcode_buffer = BytesIO()
    codigo.write(barcode_buffer)
    barcode_buffer.seek(0)

    barcode_img = ImageReader(barcode_buffer)
    carnet.drawImage(
        barcode_img,
        center_x - (40 * mm) / 2,
        5 * mm,
        width=40 * mm,
        height=10 * mm
    )

    # Finalizar PDF
    carnet.showPage()
    output = carnet.getpdfdata()
    buffer = BytesIO(output)
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='carnet.pdf')
