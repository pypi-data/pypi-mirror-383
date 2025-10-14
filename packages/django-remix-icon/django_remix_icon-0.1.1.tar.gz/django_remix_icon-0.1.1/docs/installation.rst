Installation
============

System Requirements
-------------------

* Python 3.8 or higher
* Django 3.2 or higher

Installing Django RemixIcon
---------------------------

Install from PyPI
~~~~~~~~~~~~~~~~~

The easiest way to install Django RemixIcon is using pip:

.. code-block:: bash

    pip install django-remix-icon

Install from Source
~~~~~~~~~~~~~~~~~~~

You can also install from the source code:

.. code-block:: bash

    git clone https://github.com/brktrlw/django-remix-icon.git
    cd django-remix-icon
    pip install -e .

Django Configuration
--------------------

1. Add ``django_remix_icon`` to your ``INSTALLED_APPS`` setting:

.. code-block:: python

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        # ... your other apps
        'django_remix_icon',  # Add this line
    ]

2. Include the package URLs in your project's main ``urls.py``:

.. code-block:: python

    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        path('admin/', admin.site.urls),
        # ... your other URLs
        path('remix-icon/', include('django_remix_icon.urls')),
    ]

.. note::
   The URL path can be customized to your preference. The important part is that the views are accessible for the admin autocomplete functionality.

3. Collect static files (if using Django's static file handling):

.. code-block:: bash

    python manage.py collectstatic

Static Files Configuration
--------------------------

The package includes CSS and JavaScript files for the admin widget functionality. These are automatically included when using the widget.

If you're using a custom static file configuration, ensure that the package's static files are properly served:

.. code-block:: python

    # settings.py
    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]

RemixIcon CSS
~~~~~~~~~~~~~

The package automatically includes RemixIcon CSS from CDN. No additional configuration is needed, but you can override this behavior if needed.

Verification
------------

To verify that the installation was successful:

1. Start your Django development server:

.. code-block:: bash

    python manage.py runserver

2. Visit the Django admin and create a model with an ``IconField`` (see :doc:`quickstart` for an example).

3. You should see the icon selection widget with autocomplete functionality.

Troubleshooting
---------------

Static Files Not Loading
~~~~~~~~~~~~~~~~~~~~~~~~~

If the admin widget styles or JavaScript are not loading:

1. Ensure ``django.contrib.staticfiles`` is in your ``INSTALLED_APPS``
2. Run ``python manage.py collectstatic``
3. Check that your ``STATIC_URL`` setting is correct
4. Verify that static files are properly served in your web server configuration

Autocomplete Not Working
~~~~~~~~~~~~~~~~~~~~~~~~~

If the autocomplete functionality is not working:

1. Ensure the package URLs are properly included in your URL configuration
2. Check the browser's developer tools for JavaScript errors
3. Verify that the CSRF token is properly configured for AJAX requests

URL Import Errors
~~~~~~~~~~~~~~~~~

If you encounter import errors when including the URLs:

1. Ensure ``django_remix_icon`` is in your ``INSTALLED_APPS``
2. Try restarting your Django development server
3. Check that you're using the correct import path

Next Steps
----------

Now that you have Django RemixIcon installed, continue to the :doc:`quickstart` guide to learn how to use it in your project.
