from django.db import models
from django.utils.crypto import get_random_string
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageEnhance
import requests
from io import BytesIO
from django.core.files.base import ContentFile


class Secciones(models.Model):
    Seccion=models.CharField(max_length=100)
    def __str__(self):
        return self.Seccion
    
class Grados(models.Model):
    Grado=models.CharField(max_length=100)
    def __str__(self):
        return self.Grado
    
class Tutores(models.Model):
    tutor=models.CharField(max_length=100)
    usuario = models.CharField(max_length=100, unique=True,blank=True, null=True)
    contraseña = models.CharField(max_length=100,blank=True, null=True)
    secciones=models.ManyToManyField(Secciones)
    def __str__(self):

        return self.tutor   

class Profesores(models.Model):
    profesor=models.CharField(max_length=100)
    usuario = models.CharField(max_length=100, unique=True,blank=True, null=True)
    contraseña = models.CharField(max_length=100,blank=True, null=True)
    secciones=models.ManyToManyField(Secciones)
    def __str__(self):

        return self.profesor
    
class Apoderados(models.Model):
    Apoderado=models.CharField(max_length=100)
    usuario = models.CharField(max_length=100, unique=True,blank=True, null=True)
    contraseña = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.Apoderado  

class Mensajes(models.Model):
    contenido=models.TextField(blank=True, null=True)  
    profesor=models.ForeignKey(Profesores, on_delete=models.CASCADE,blank=True, null=True)
    apoderado=models.ForeignKey(Apoderados, on_delete=models.CASCADE,blank=True, null=True)  
    fecha=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.contenido      
    

class Estudiante(models.Model):
    matricula=models.CharField(max_length=350, blank=True, null=True)
    nombres=models.CharField(max_length=350, blank=True, null=True)
    apellido=models.CharField(max_length=350, blank=True, null=True)
    nombrecompleto = models.CharField(max_length=350, blank=True, null=True)
    tipodocumento=models.CharField(max_length=100, blank=True, null=True)
    dni=models.CharField(max_length=12, blank=True, null=True)
    grado=models.ForeignKey(Grados, on_delete=models.CASCADE,blank=True, null=True)
    sexo=models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos/', blank=True, null=True)
    codigo_qr = models.ImageField(upload_to='codigos_qr/', blank=True, null=True)
    aula=models.ForeignKey(Secciones, on_delete=models.CASCADE,blank=True, null=True)
    apoderado=models.ForeignKey(Apoderados, on_delete=models.CASCADE,blank=True, null=True)
    fecha_nacimiento=models.DateField(blank=True, null=True)
    nacionalidad=models.CharField(max_length=70, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.matricula:
            self.matricula = get_random_string(10)

        # Generar código QR ddd
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(self.matricula)
        qr.make(fit=True)

        # Personalizar el diseño del código QR
        qr_image = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=(0, 0, 0))
        ).convert('RGBA')  # Convertir a RGBA para manejar transparencias

        # URL del logotipo
        logo_url = 'https://res.cloudinary.com/dream-music/image/upload/v1739577892/nuevologo_g81gus.png'

        try:
            response = requests.get(logo_url, stream=True)
            if response.status_code == 200:
                logo = Image.open(BytesIO(response.content)).convert('RGBA')

                # Calcular tamaño del logotipo (15% del QR)
                qr_width, qr_height = qr_image.size
                logo_size = int(qr_width * 0.15)
                logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

                # Aplicar transparencia al logotipo
                if logo.mode == "RGBA":
                    alpha = logo.split()[3]
                    alpha = ImageEnhance.Brightness(alpha).enhance(0.5)
                    logo.putalpha(alpha)

                # Centrar logotipo
                pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                qr_image.paste(logo, pos, mask=logo)
            else:
                print(f"Error al descargar el logotipo: {response.status_code}")
        except Exception as e:
            print(f"Error al procesar el logotipo: {e}")

        # Guardar la imagen en el campo codigo_qr
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        self.codigo_qr.save(f"{self.matricula}.png", ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.dni} - {self.nombrecompleto}"

class Asistencia(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Asistencia de {self.estudiante.nombre} - {self.fecha_hora}"