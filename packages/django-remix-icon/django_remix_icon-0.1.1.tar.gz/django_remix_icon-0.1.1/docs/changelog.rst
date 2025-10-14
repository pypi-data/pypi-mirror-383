Changelog
=========

All notable changes to Django RemixIcon will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

[0.1.0] - 2025-01-XX
--------------------

Initial release of Django RemixIcon.

Added
~~~~~

**Core Features:**

- ``IconField`` - Custom Django model field for storing RemixIcon names
- ``IconFormField`` - Form field with validation for RemixIcon selection
- ``IconSelectWidget`` - Admin widget with autocomplete and icon preview
- ``IconPreviewWidget`` - Simple widget for icon preview without autocomplete

**Template Tags:**

- ``remix_icon`` - Main template tag for rendering icons
- ``remix_icon_css`` - Template tag for including RemixIcon CSS
- ``remix_icon_version`` - Template tag for getting RemixIcon version
- ``remix_icon_with_text`` - Inclusion tag for icons with text
- ``remix_icon_list`` - Template tag for getting filtered icon lists
- ``is_remix_icon`` - Template filter for validating icon names

**Admin Integration:**

- Seamless Django admin integration
- Full support for inline models
- Autocomplete functionality with search
- Live icon preview in admin forms
- Keyboard navigation support

**JavaScript Features:**

- Debounced search input for performance
- AJAX-powered autocomplete
- Keyboard navigation (arrow keys, enter, escape)
- Dynamic widget initialization
- Support for Django admin inline forms

**CSS Styling:**

- Complete CSS styling for admin widgets
- Responsive design for mobile devices
- Dark mode support
- Customizable widget appearance
- Bootstrap and Tailwind CSS compatibility examples

**Documentation:**

- Comprehensive Sphinx documentation
- ReadTheDocs.io configuration
- Installation guide with troubleshooting
- Quick start tutorial
- Detailed usage instructions
- Template tags reference
- Customization guide
- Complete API documentation

**Package Features:**

- PyPI-ready package configuration
- Proper Django app structure
- Static file management
- URL configuration for AJAX endpoints
- Migration support
- Validation and error handling

**RemixIcon Integration:**

- RemixIcon v4.7.0 support
- 2000+ icons available
- Categorized icon organization
- CDN-based CSS inclusion
- Icon name validation

**Browser Support:**

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

**Django Compatibility:**

- Django 3.2+
- Python 3.8+

Security
~~~~~~~~

- XSS protection in template tags
- CSRF protection for AJAX requests
- Input validation and sanitization
- Safe HTML rendering

Performance
~~~~~~~~~~~

- Efficient icon search and filtering
- Debounced search input (150ms)
- Cached icon lists
- Lazy loading support
- Minimal JavaScript footprint

Changed
~~~~~~~

N/A - Initial release

Deprecated
~~~~~~~~~~

N/A - Initial release

Removed
~~~~~~~

N/A - Initial release

Fixed
~~~~~

N/A - Initial release

Security
~~~~~~~~

N/A - Initial release

---

Migration Guides
================

From 0.0.x to 0.1.0
-------------------

This is the initial stable release. No migration needed.

---

Breaking Changes
================

Version 0.1.0
--------------

No breaking changes - initial release.

---

Upgrade Instructions
====================

General Upgrade Process
-----------------------

1. **Backup your database** before upgrading
2. **Update the package:**

   .. code-block:: bash

       pip install --upgrade django-remix-icon

3. **Run migrations** if any are provided:

   .. code-block:: bash

       python manage.py migrate

4. **Collect static files:**

   .. code-block:: bash

       python manage.py collectstatic

5. **Test your application** thoroughly

---


Supported Versions
------------------

Currently supported versions:

- **Django RemixIcon 0.1.x**: Full support, regular updates
- **Django 3.2+**: Fully supported
- **Python 3.8+**: Fully supported

End of Life Schedule
--------------------

- Django RemixIcon follows Django's support lifecycle
- Each major version is supported for 2 years minimum
- Security updates provided for 1 year after EOL

---

Contributing to Changelog
=========================

When contributing changes, please:

1. Add entries to the [Unreleased] section
2. Follow the format: **Type** - Description (GitHub issue #)
3. Use these types:
   - **Added** for new features
   - **Changed** for changes in existing functionality
   - **Deprecated** for soon-to-be removed features
   - **Removed** for now removed features
   - **Fixed** for any bug fixes
   - **Security** for vulnerability fixes

Example entry:

.. code-block:: text

    Added
    ~~~~~
    - **Widget** - Added keyboard shortcut support for icon selection (#123)
    - **Template Tag** - New ``remix_icon_search`` template tag for dynamic search (#456)

    Fixed
    ~~~~~
    - **Widget** - Fixed autocomplete not working in Safari (#789)
    - **Admin** - Fixed inline widget initialization in Django 4.2 (#012)
