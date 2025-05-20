from django import template

register = template.Library()

# @register.filter(name='replace_comma')
# def replace_comma(value):
#     return value.replace(',', '.')

@register.filter
def replace_comma(value):
    if isinstance(value, str):
        return value.replace(',', '.')
    return str(value).replace(',', '.')

@register.filter
def multiplicar(valor1, valor2):
    try:
        resultado = float(valor1) * float(valor2)
        return f"{resultado:.2f}"  # Formatear con dos decimales y punto como separador
    except (ValueError, TypeError):
        return "0.00"  # Retorna 0.00 en caso de error