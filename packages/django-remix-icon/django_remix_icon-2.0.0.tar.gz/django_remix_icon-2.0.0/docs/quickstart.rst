Quick Start Guide
=================

This guide will help you get started with Django RemixIcon in minutes.

Creating Your First Icon Field
-------------------------------

1. **Create a model with an IconField**:

.. code-block:: python

    # models.py
    from django.db import models
    from django_remix_icon.fields import IconField

    class MenuItem(models.Model):
        name = models.CharField(max_length=100)
        url = models.URLField()
        icon = IconField(blank=True, null=True)
        is_active = models.BooleanField(default=True)

        def __str__(self):
            return self.name

        class Meta:
            verbose_name = "Menu Item"
            verbose_name_plural = "Menu Items"

2. **Register the model in admin**:

.. code-block:: python

    # admin.py
    from django.contrib import admin
    from .models import MenuItem

    @admin.register(MenuItem)
    class MenuItemAdmin(admin.ModelAdmin):
        list_display = ('name', 'url', 'icon', 'is_active')
        list_filter = ('is_active',)
        search_fields = ('name',)

3. **Create and run migrations**:

.. code-block:: bash

    python manage.py makemigrations
    python manage.py migrate

Using in Templates
------------------

1. **Load the template tags**:

.. code-block:: html

    {% load remix_icon_tags %}

2. **Include RemixIcon CSS** (add this once in your base template):

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head>
        <title>My Site</title>
        {% remix_icon_css %}
    </head>
    <body>
        <!-- Your content -->
    </body>
    </html>

3. **Render icons in your templates**:

.. code-block:: html

    <!-- Simple icon rendering -->
    {% remix_icon 'ri-home-line' %}

    <!-- Using model field -->
    {% for item in menu_items %}
        <div class="menu-item">
            {% remix_icon item.icon %}
            <a href="{{ item.url }}">{{ item.name }}</a>
        </div>
    {% endfor %}

    <!-- With custom attributes -->
    {% remix_icon 'ri-heart-fill' class='text-red-500' size='24' %}

Working with Inline Models
---------------------------

The IconField works seamlessly with Django admin inline models:

.. code-block:: python

    # models.py
    class NavigationMenu(models.Model):
        name = models.CharField(max_length=100)

    class NavigationMenuItem(models.Model):
        menu = models.ForeignKey(NavigationMenu, on_delete=models.CASCADE)
        title = models.CharField(max_length=100)
        icon = IconField()
        order = models.PositiveIntegerField(default=0)

    # admin.py
    class NavigationMenuItemInline(admin.TabularInline):
        model = NavigationMenuItem
        extra = 1
        fields = ('title', 'icon', 'order')

    @admin.register(NavigationMenu)
    class NavigationMenuAdmin(admin.ModelAdmin):
        inlines = [NavigationMenuItemInline]

Complete Example
----------------

Here's a complete working example for a blog with icon categories:

**models.py**:

.. code-block:: python

    from django.db import models
    from django_remix_icon.fields import IconField

    class Category(models.Model):
        name = models.CharField(max_length=50)
        icon = IconField(help_text="Choose an icon for this category")
        description = models.TextField(blank=True)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return self.name

        class Meta:
            verbose_name_plural = "Categories"

    class Post(models.Model):
        title = models.CharField(max_length=200)
        content = models.TextField()
        category = models.ForeignKey(Category, on_delete=models.CASCADE)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return self.title

**admin.py**:

.. code-block:: python

    from django.contrib import admin
    from .models import Category, Post

    @admin.register(Category)
    class CategoryAdmin(admin.ModelAdmin):
        list_display = ('name', 'icon', 'created_at')
        search_fields = ('name',)

    @admin.register(Post)
    class PostAdmin(admin.ModelAdmin):
        list_display = ('title', 'category', 'created_at')
        list_filter = ('category', 'created_at')
        search_fields = ('title', 'content')

**Template (blog/category_list.html)**:

.. code-block:: html

    {% load remix_icon_tags %}

    <!DOCTYPE html>
    <html>
    <head>
        <title>Blog Categories</title>
        {% remix_icon_css %}
        <style>
            .category-card {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
                margin: 10px;
                display: inline-block;
                text-align: center;
                min-width: 200px;
            }
            .category-icon {
                font-size: 48px;
                color: #007cba;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <h1>Blog Categories</h1>

        <div class="categories">
            {% for category in categories %}
                <div class="category-card">
                    <div class="category-icon">
                        {% remix_icon category.icon size='48' %}
                    </div>
                    <h3>{{ category.name }}</h3>
                    <p>{{ category.description }}</p>
                    <small>{{ category.post_set.count }} posts</small>
                </div>
            {% endfor %}
        </div>
    </body>
    </html>

**views.py**:

.. code-block:: python

    from django.shortcuts import render
    from .models import Category

    def category_list(request):
        categories = Category.objects.all()
        return render(request, 'blog/category_list.html', {
            'categories': categories
        })

Testing the Setup
-----------------

1. **Start the development server**:

.. code-block:: bash

    python manage.py runserver

2. **Visit the Django admin** at ``http://localhost:8000/admin/``

3. **Create a new category**:
   - Click "Add" next to Categories
   - Enter a name
   - Click in the Icon field - you should see an autocomplete widget
   - Start typing "home" and select an icon like "ri-home-line"
   - Save the category

4. **View your categories** in the frontend by visiting your category list view

Expected Results
----------------

- **In Django Admin**: You should see an icon field with autocomplete functionality and icon preview
- **In Templates**: Icons should render as proper RemixIcon symbols
- **Autocomplete**: Should work smoothly with search functionality
- **Inline Models**: Should work identically to regular form fields

Next Steps
----------

Now that you have the basics working, explore:

- :doc:`usage` - Detailed usage instructions
- :doc:`template_tags` - All available template tags and their options
- :doc:`customization` - Customizing the widget appearance and behavior
