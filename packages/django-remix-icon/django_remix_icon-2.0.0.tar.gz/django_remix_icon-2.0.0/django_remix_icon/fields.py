"""
Django model fields for RemixIcon integration.
"""

from django import forms
from django.db import models
from django.core.exceptions import ValidationError

from django_remix_icon.remix_icons import REMIX_ICONS
from django_remix_icon.widgets import IconSelectWidget


def get_all_icon_names():
    """
    Get a flat list of all icon names with 'ri-' prefix.
    """
    icon_names = []
    for category, icons in REMIX_ICONS.items():
        for icon_name in icons.keys():
            icon_names.append(f"ri-{icon_name}")
    return icon_names


def get_icon_choices_list():
    """
    Get choices list for form field.
    """
    choices = []
    for category, icons in REMIX_ICONS.items():
        for icon_name in icons.keys():
            full_name = f"ri-{icon_name}"
            label = icon_name.replace('-', ' ').title()
            choices.append((full_name, label))
    return choices


class IconFormField(forms.ChoiceField):
    """
    Form field for selecting RemixIcons with autocomplete functionality.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', get_icon_choices_list())
        kwargs.setdefault('widget', IconSelectWidget())
        super().__init__(*args, **kwargs)

    def validate(self, value):
        """
        Validate that the selected icon is a valid RemixIcon.
        """
        if value and value not in get_all_icon_names():
            raise ValidationError(f"'{value}' is not a valid RemixIcon name.")
        super().validate(value)


class IconField(models.CharField):
    """
    A Django model field for storing RemixIcon names.

    This field stores the icon name as a string and provides
    a custom form field with autocomplete functionality in Django admin.

    Usage:
        class MyModel(models.Model):
            icon = IconField()
    """

    description = "A field for storing RemixIcon names"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 100)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('null', True)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """
        Return the appropriate form field for this model field.
        """
        defaults = {'form_class': forms.CharField}
        defaults.update(kwargs)

        field = super().formfield(**defaults)

        field.widget = IconSelectWidget()

        return field

    def validate(self, value, model_instance):
        """
        Validate that the stored value is a valid RemixIcon name.
        """
        super().validate(value, model_instance)
        if value and value not in get_all_icon_names():
            raise ValidationError(f"'{value}' is not a valid RemixIcon name.")

    def deconstruct(self):
        """
        Return details needed to recreate the field.
        """
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get('max_length') == 100:
            del kwargs['max_length']
        return name, path, args, kwargs
