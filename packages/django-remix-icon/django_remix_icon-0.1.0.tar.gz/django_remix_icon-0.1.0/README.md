# Django RemixIcon

[![PyPI version](https://badge.fury.io/py/django-remix-icon.svg)](https://badge.fury.io/py/django-remix-icon)
[![Python versions](https://img.shields.io/pypi/pyversions/django-remix-icon.svg)](https://pypi.org/project/django-remix-icon/)
[![Django versions](https://img.shields.io/pypi/djversions/django-remix-icon.svg)](https://pypi.org/project/django-remix-icon/)
[![License](https://img.shields.io/pypi/l/django-remix-icon.svg)](https://github.com/brktrlw/django-remix-icon/blob/main/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/django-remix-icon/badge/?version=latest)](https://django-remix-icon.readthedocs.io/en/latest/)

A simple Django package for integrating [RemixIcon](https://remixicon.com/) with Django admin and templates. Provides seamless icon selection with autocomplete, preview functionality, and template tags for easy icon rendering.

## ✨ Features

- **🎯 Simple Integration**: Minimal configuration required
- **🔍 Autocomplete Widget**: Fast icon search in Django admin
- **👁️ Live Preview**: See icons as you type
- **📋 Template Tags**: Easy icon rendering in templates
- **📱 Responsive**: Works on mobile and desktop
- **⚡ Performance**: Efficient search and caching
- **🎨 Customizable**: Style to match your design
- **🔧 Inline Support**: Works with Django admin inlines
- **🌙 Dark Mode**: Supports dark themes

## 🚀 Quick Start

### Installation

```bash
pip install django-remix-icon
```

### Django Setup

Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... your other apps
    'django_remix_icon',
]
```

Include URLs in your project:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/remix-icon/', include('django_remix_icon.urls')),
    # ... your other URLs
]
```

### Basic Usage

**In your models:**

```python
from django.db import models
from django_remix_icon.fields import IconField

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    icon = IconField()  # Simple icon field
    url = models.URLField()

class Category(models.Model):
    title = models.CharField(max_length=100)
    icon = IconField(blank=True, null=True)  # Optional icon
```

**In your templates:**

```html
{% load remix_icon_tags %}

<!DOCTYPE html>
<html>
<head>
    <title>My Site</title>
    {% remix_icon_css %}  <!-- Include RemixIcon CSS -->
</head>
<body>
    <!-- Simple icon rendering -->
    <h1>{% remix_icon 'ri-home-line' %} Welcome</h1>

    <!-- Using model fields -->
    {% for item in menu_items %}
        <a href="{{ item.url }}">
            {% remix_icon item.icon %}
            {{ item.name }}
        </a>
    {% endfor %}

    <!-- With custom styling -->
    {% remix_icon 'ri-heart-fill' class='text-red-500' size='24' %}
</body>
</html>
```

**Admin Integration:**

```python
# admin.py - No additional configuration needed!
from django.contrib import admin
from .models import MenuItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'url')
    # IconField automatically provides autocomplete widget
```

## 📖 Documentation

**Complete documentation is available at [django-remix-icon.readthedocs.io](https://django-remix-icon.readthedocs.io/)**

- [Installation Guide](https://django-remix-icon.readthedocs.io/en/latest/installation.html)
- [Quick Start Tutorial](https://django-remix-icon.readthedocs.io/en/latest/quickstart.html)
- [Template Tags Reference](https://django-remix-icon.readthedocs.io/en/latest/template_tags.html)
- [Customization Guide](https://django-remix-icon.readthedocs.io/en/latest/customization.html)
- [API Documentation](https://django-remix-icon.readthedocs.io/en/latest/api/)

## 🎭 Template Tags

Django RemixIcon provides several template tags for flexible icon rendering:

```html
{% load remix_icon_tags %}

<!-- Basic icon -->
{% remix_icon 'ri-star-line' %}

<!-- Icon with attributes -->
{% remix_icon 'ri-heart-fill' class='love-icon' size='20' %}

<!-- Icon with text -->
{% remix_icon_with_text 'ri-download-line' 'Download' class='btn' %}

<!-- Conditional rendering -->
{% if item.icon|is_remix_icon %}
    {% remix_icon item.icon %}
{% endif %}

<!-- Get icon lists -->
{% remix_icon_list category='user' limit=10 as user_icons %}
{% for icon in user_icons %}
    {% remix_icon icon %}
{% endfor %}
```

## 🎨 Admin Widget Features

The Django admin integration provides:

### Autocomplete Search
- **Fast Search**: Find icons quickly by typing
- **Smart Filtering**: Matches icon names and categories
- **Keyboard Navigation**: Use arrow keys and Enter

### Live Preview
- **Visual Feedback**: See icons as you select them
- **Icon Information**: Shows icon name and category
- **Responsive Design**: Works on all screen sizes

### Django Integration
- **No Configuration**: Works out of the box
- **Inline Support**: Works with `TabularInline` and `StackedInline`
- **Validation**: Ensures only valid icons are selected

## 🔧 Customization

### Custom Widget Styling

```css
/* Custom styles for your theme */
.remix-icon-widget {
    max-width: 500px;
}

.icon-search-input {
    border-radius: 8px;
    padding: 12px 16px;
}

.icon-preview {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 8px;
}
```

### Custom Form Field

```python
from django import forms
from django_remix_icon.fields import IconFormField

class CustomForm(forms.Form):
    icon = IconFormField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget.attrs.update({
            'class': 'my-custom-icon-widget'
        })
```

## 📱 Examples

### Navigation Menu

```python
# models.py
class NavigationItem(models.Model):
    title = models.CharField(max_length=100)
    icon = IconField()
    url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
```

```html
<!-- template.html -->
{% load remix_icon_tags %}

<nav class="main-nav">
    {% for item in navigation_items %}
        <a href="{{ item.url }}" class="nav-item">
            {% remix_icon item.icon class='nav-icon' %}
            <span>{{ item.title }}</span>
        </a>
    {% endfor %}
</nav>
```

### Dashboard Cards

```python
# models.py
class DashboardCard(models.Model):
    title = models.CharField(max_length=100)
    icon = IconField()
    description = models.TextField()
    value = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='blue')
```

```html
<!-- dashboard.html -->
{% for card in dashboard_cards %}
    <div class="dashboard-card card-{{ card.color }}">
        <div class="card-icon">
            {% remix_icon card.icon size='32' %}
        </div>
        <div class="card-content">
            <h3>{{ card.title }}</h3>
            <p class="card-value">{{ card.value }}</p>
            <p class="card-description">{{ card.description }}</p>
        </div>
    </div>
{% endfor %}
```

### Status Indicators

```html
{% for task in tasks %}
    <div class="task-item">
        {% if task.completed %}
            {% remix_icon 'ri-check-circle-fill' class='text-green-500' %}
        {% elif task.in_progress %}
            {% remix_icon 'ri-time-line' class='text-blue-500' %}
        {% else %}
            {% remix_icon 'ri-circle-line' class='text-gray-400' %}
        {% endif %}
        <span>{{ task.name }}</span>
    </div>
{% endfor %}
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://django-remix-icon.readthedocs.io/en/latest/contributing.html) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/brktrlw/django-remix-icon.git
cd django-remix-icon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]
```

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run code formatting (black, isort, flake8)
5. Commit your changes (`git commit -am 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📋 Requirements

- **Python**: 3.8+
- **Django**: 3.2+
- **Browser**: Chrome 60+, Firefox 55+, Safari 12+, Edge 79+

## 🔄 Compatibility

| Django Version | Python Version | Status |
|----------------|----------------|--------|
| 5.0            | 3.10, 3.11, 3.12 | ✅ Supported |
| 4.2 (LTS)      | 3.8, 3.9, 3.10, 3.11, 3.12 | ✅ Supported |
| 4.1            | 3.8, 3.9, 3.10, 3.11 | ✅ Supported |
| 4.0            | 3.8, 3.9, 3.10, 3.11 | ✅ Supported |
| 3.2 (LTS)      | 3.8, 3.9, 3.10, 3.11 | ✅ Supported |

## 🏗️ Architecture

```
django-remix-icon/
├── django_remix_icon/
│   ├── fields.py          # IconField model field
│   ├── widgets.py         # Admin widgets
│   ├── views.py           # AJAX search views
│   ├── templatetags/      # Template tags
│   ├── static/            # CSS and JavaScript
│   └── templates/         # Widget templates
├── docs/                  # Documentation
└── examples/              # Usage examples
```

## 🎯 Philosophy

Django RemixIcon follows these principles:

- **Simplicity**: Minimal configuration, maximum functionality
- **Performance**: Efficient search and rendering
- **Flexibility**: Customizable but with sensible defaults
- **Integration**: Seamless Django admin experience
- **Accessibility**: Keyboard navigation and screen reader support

## 🔍 FAQ

**Q: How many icons are available?**
A: Over 2,000 icons from RemixIcon v4.7.0, covering all major categories.

**Q: Does it work with Django admin inlines?**
A: Yes! The widget works perfectly with both TabularInline and StackedInline.

**Q: Can I customize the widget appearance?**
A: Absolutely! The widget includes CSS classes for easy customization.

**Q: Is there a performance impact?**
A: Minimal. The widget uses debounced search and efficient caching.

**Q: Does it work on mobile?**
A: Yes, the widget is fully responsive and touch-friendly.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [RemixIcon](https://remixicon.com/) for the amazing icon library
- [Django](https://www.djangoproject.com/) for the excellent web framework
- All [contributors](https://github.com/brktrlw/django-remix-icon/graphs/contributors) who help improve this package

## 📈 Changelog

See [CHANGELOG.md](https://django-remix-icon.readthedocs.io/en/latest/changelog.html) for a list of changes and migration guides.

## 🔗 Links

- **Documentation**: https://django-remix-icon.readthedocs.io/
- **PyPI**: https://pypi.org/project/django-remix-icon/
- **GitHub**: https://github.com/brktrlw/django-remix-icon
- **Issues**: https://github.com/brktrlw/django-remix-icon/issues
- **RemixIcon**: https://remixicon.com/

---

<div align="center">

**[⭐ Star this repo](https://github.com/brktrlw/django-remix-icon) if you find it useful!**

Made with ❤️ for the Django community

</div>
