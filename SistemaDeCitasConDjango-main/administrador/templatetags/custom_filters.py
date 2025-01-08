# myapp/templatetags/custom_filters.py
from django import template
from django import forms


register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


@register.filter(name='add_class')
def add_class(value, css_class):
    if hasattr(value.field.widget, 'attrs'):
        if not isinstance(value.field.widget, forms.CheckboxInput):
            value.field.widget.attrs['class'] = css_class
    return value


from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """Añade una clase CSS a un campo de formulario."""
    # Verifica si el valor tiene el atributo 'field', lo cual indica que es un campo de formulario
    if hasattr(value, 'field') and hasattr(value.field.widget, 'attrs'):
        widget_attrs = value.field.widget.attrs
        current_classes = widget_attrs.get('class', '')
        new_classes = f'{current_classes} {arg}'.strip()
        widget_attrs['class'] = new_classes
        return value
    # Si no es un campo de formulario, devuelve el valor tal cual
    return value

