"""
Django widgets for RemixIcon selection.
"""

import json
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe

from django_remix_icon.remix_icons import REMIX_ICONS


def get_all_icon_names():
    """
    Get a flat list of all icon names with 'ri-' prefix.
    """
    icon_names = []
    for category, icons in REMIX_ICONS.items():
        for icon_name in icons.keys():
            icon_names.append(f"ri-{icon_name}")
    return icon_names


class IconSelectWidget(forms.Select):
    """
    A custom widget for selecting RemixIcons with autocomplete and preview functionality.

    This widget provides:
    - Autocomplete functionality for searching icons
    - Icon preview in the dropdown
    - Clean integration with Django admin
    """

    class Media:
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/remixicon@4.7.0/fonts/remixicon.css',
                'django_remix_icon/css/icon_select.css',
            )
        }
        js = ('django_remix_icon/js/icon_select.js',)

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.choices = [(icon, icon) for icon in get_all_icon_names()]

    def format_value(self, value):
        """
        Return the value that should be displayed in the widget.
        """
        if value is None:
            return ''
        return str(value)

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the widget as HTML.
        """
        if attrs is None:
            attrs = {}

        field_id = attrs.get('id', f'id_{name}')

        preview_html = ''
        if value:
            preview_html = f'''
            <div class="icon-preview" id="icon-preview-{name}">
                <i class="{value}"></i>
                <span class="icon-name">{value}</span>
            </div>
            '''
        else:
            preview_html = f'''
            <div class="icon-preview" id="icon-preview-{name}" style="display: none;">
                <i class=""></i>
                <span class="icon-name"></span>
            </div>
            '''

        # Create a hidden input to store the actual value
        # This is what Django will use to save the data
        hidden_attrs = {
            'type': 'hidden',
            'name': name,
            'id': field_id,
            'value': value or '',
        }
        hidden_attrs_str = ' '.join([f'{k}="{v}"' for k, v in hidden_attrs.items()])

        # Get the search URL
        search_url = reverse('django_remix_icon:icon_search')

        # Combine HTML with autocomplete container
        html = f'''
        <div class="remix-icon-widget" data-field-name="{name}">
            <input {hidden_attrs_str}>
            <div class="icon-search-container">
                <input type="text" class="icon-search-input"
                       placeholder="Search RemixIcons..."
                       data-target="{field_id}"
                       data-icon-search-url="{search_url}"
                       autocomplete="off"
                       value="{value or ''}">
                <div class="icon-search-results" id="search-results-{name}"></div>
            </div>
            {preview_html}
        </div>
        '''

        return mark_safe(html)


class IconPreviewWidget(forms.TextInput):
    """
    A simpler widget that shows icon preview without autocomplete.
    Useful for read-only displays or simple forms.
    """

    class Media:
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/remixicon@4.7.0/fonts/remixicon.css',
                'django_remix_icon/css/icon_preview.css',
            )
        }

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the widget with icon preview.
        """
        if attrs is None:
            attrs = {}

        attrs['class'] = attrs.get('class', '') + ' remix-icon-preview-input'

        input_html = super().render(name, value, attrs, renderer)

        preview_html = ''
        if value:
            preview_html = f'''
            <div class="icon-preview-simple">
                <i class="{value}"></i>
                <span class="icon-name">{value}</span>
            </div>
            '''

        html = f'''
        <div class="remix-icon-preview-widget">
            {input_html}
            {preview_html}
        </div>
        '''

        return mark_safe(html)
