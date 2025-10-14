"""
Template tags for rendering RemixIcons in Django templates.
"""

from django import template
from django.utils.safestring import mark_safe

from django_remix_icon.remix_icons import REMIX_ICONS

register = template.Library()


def get_all_icon_names():
    """
    Get a flat list of all icon names with 'ri-' prefix.
    """
    icon_names = []
    for category, icons in REMIX_ICONS.items():
        for icon_name in icons.keys():
            icon_names.append(f"ri-{icon_name}")
    return icon_names


@register.simple_tag
def remix_icon(icon_name, **kwargs):
    """
    Render a RemixIcon with optional attributes.

    Usage:
        {% remix_icon 'ri-home-line' %}
        {% remix_icon 'ri-user-fill' class='text-blue-500' size='24' %}
        {% remix_icon instance.icon_field %}
        {% remix_icon 'ri-heart-line' style='color: red; font-size: 20px;' %}

    Args:
        icon_name: The RemixIcon name (e.g., 'ri-home-line')
        **kwargs: Additional HTML attributes (class, style, size, etc.)

    Returns:
        HTML <i> tag with the icon
    """
    if not icon_name:
        return ''

    # Validate icon name
    if icon_name not in get_all_icon_names():
        # Return empty or a placeholder for invalid icons
        return mark_safe(f'<i class="ri-question-line" title="Invalid icon: {icon_name}"></i>')

    # Build attributes
    attrs = {}

    # Handle CSS classes
    css_classes = [icon_name]
    if 'class' in kwargs:
        css_classes.append(kwargs.pop('class'))
    attrs['class'] = ' '.join(css_classes)

    # Handle size attribute (convert to font-size style)
    if 'size' in kwargs:
        size = kwargs.pop('size')
        try:
            # If size is numeric, add 'px'
            if isinstance(size, (int, float)) or size.isdigit():
                size = f"{size}px"

            style = attrs.get('style', '')
            if style and not style.endswith(';'):
                style += ';'
            style += f"font-size: {size};"
            attrs['style'] = style
        except (ValueError, AttributeError):
            pass  # Invalid size, ignore

    # Add any remaining attributes
    for key, value in kwargs.items():
        attrs[key] = value

    # Build the HTML tag
    attr_string = ''
    for key, value in attrs.items():
        attr_string += f' {key}="{value}"'

    return mark_safe(f'<i{attr_string}></i>')


@register.simple_tag
def remix_icon_css():
    """
    Include RemixIcon CSS from CDN.

    Usage:
        {% remix_icon_css %}

    Returns:
        HTML link tag for RemixIcon CSS
    """
    return mark_safe(
        '<link href="https://cdn.jsdelivr.net/npm/remixicon@4.7.0/fonts/remixicon.css" rel="stylesheet">'
    )


@register.simple_tag
def remix_icon_version():
    """
    Get the RemixIcon version being used.

    Usage:
        {% remix_icon_version %}

    Returns:
        Version string
    """
    return "4.7.0"


@register.filter
def is_remix_icon(icon_name):
    """
    Check if a string is a valid RemixIcon name.

    Usage:
        {% if icon_field|is_remix_icon %}
            {% remix_icon icon_field %}
        {% endif %}

    Args:
        icon_name: The icon name to check

    Returns:
        Boolean indicating if the icon name is valid
    """
    if not icon_name:
        return False
    return icon_name in get_all_icon_names()


@register.inclusion_tag('django_remix_icon/icon_with_text.html')
def remix_icon_with_text(icon_name, text, **kwargs):
    """
    Render an icon with accompanying text.

    Usage:
        {% remix_icon_with_text 'ri-home-line' 'Home' %}
        {% remix_icon_with_text instance.icon 'Click here' class='btn btn-primary' %}

    Args:
        icon_name: The RemixIcon name
        text: Text to display alongside the icon
        **kwargs: Additional HTML attributes for the container

    Returns:
        Rendered template with icon and text
    """
    return {
        'icon_name': icon_name,
        'text': text,
        'attrs': kwargs,
        'is_valid_icon': icon_name in get_all_icon_names() if icon_name else False,
    }


@register.simple_tag
def remix_icon_list(category=None, limit=None):
    """
    Get a list of RemixIcon names, optionally filtered by category.

    Usage:
        {% remix_icon_list as all_icons %}
        {% remix_icon_list category='Arrows' limit=10 as arrow_icons %}
        {% remix_icon_list category='user' limit=10 as user_icons %}

    Args:
        category: Filter icons by category name or search in icon names (optional)
        limit: Limit number of icons returned (optional)

    Returns:
        List of icon names (with 'ri-' prefix)
    """
    icons = []

    # If category is specified, try to match exact category name first
    if category:
        category_str = str(category)
        # Check if it matches an exact category name
        if category_str in REMIX_ICONS:
            # Return icons from that specific category
            for icon_name in REMIX_ICONS[category_str].keys():
                icons.append(f"ri-{icon_name}")
        else:
            # Otherwise, search in icon names and category names
            category_lower = category_str.lower()
            for cat_name, cat_icons in REMIX_ICONS.items():
                # Check if category name matches
                if category_lower in cat_name.lower():
                    for icon_name in cat_icons.keys():
                        icons.append(f"ri-{icon_name}")
                else:
                    # Check individual icon names
                    for icon_name in cat_icons.keys():
                        if category_lower in icon_name.lower():
                            icons.append(f"ri-{icon_name}")
    else:
        # No category filter, return all icons
        for cat_icons in REMIX_ICONS.values():
            for icon_name in cat_icons.keys():
                icons.append(f"ri-{icon_name}")

    if limit:
        try:
            limit = int(limit)
            icons = icons[:limit]
        except (ValueError, TypeError):
            pass  # Invalid limit, return all

    return icons
