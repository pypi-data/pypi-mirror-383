Contributing
============

We welcome contributions to Django RemixIcon! This guide will help you get started.

Getting Started
---------------

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   .. code-block:: bash

       git clone https://github.com/brktrlw/django-remix-icon.git
       cd django-remix-icon

3. **Create a virtual environment:**

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate

4. **Install dependencies:**

   .. code-block:: bash

       pip install -e .
       pip install -r requirements-dev.txt

Development Setup
-----------------

**Install development dependencies:**

.. code-block:: bash

    pip install -e ".[dev]"

**Run linting:**

.. code-block:: bash

    flake8 django_remix_icon/
    black django_remix_icon/
    isort django_remix_icon/

**Build documentation:**

.. code-block:: bash

    cd docs/
    make html

Types of Contributions
----------------------

Bug Reports
~~~~~~~~~~~

When reporting bugs, please include:

- Django version
- Python version
- Browser (for widget issues)
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)

Feature Requests
~~~~~~~~~~~~~~~~

For new features:

- Describe the use case
- Explain why it would be useful
- Consider backward compatibility
- Provide examples if possible

Code Contributions
~~~~~~~~~~~~~~~~~~

We welcome:

- Bug fixes
- New features
- Performance improvements
- Documentation improvements

Code Style
----------

**Python Code:**

- Follow PEP 8
- Use Black for formatting
- Use isort for import sorting
- Maximum line length: 88 characters
- Use type hints where appropriate

**JavaScript Code:**

- Use ES6+ features
- Follow standard JavaScript conventions
- Add comments for complex logic
- Test in multiple browsers

**CSS Code:**

- Use BEM methodology when appropriate
- Mobile-first responsive design
- Support for dark mode
- Consistent indentation (2 spaces)

**Documentation:**

- Use reStructuredText format
- Include code examples
- Update API documentation for changes
- Verify examples for accuracy

Pull Request Process
--------------------

1. **Create a feature branch:**

   .. code-block:: bash

       git checkout -b feature/your-feature-name

2. **Make your changes:**

   - Write code following our style guide
   - Update documentation if necessary

3. **Run code quality checks:**

   .. code-block:: bash

       flake8 django_remix_icon/
       black --check django_remix_icon/
       isort --check-only django_remix_icon/

4. **Commit your changes:**

   .. code-block:: bash

       git add .
       git commit -m "Add feature: description of your changes"

5. **Push to your fork:**

   .. code-block:: bash

       git push origin feature/your-feature-name

6. **Create a pull request** on GitHub

**Pull Request Guidelines:**

- Provide a clear description of changes
- Reference any related issues
- Update documentation as needed
- Keep pull requests focused and atomic

Code Review Process
-------------------

All pull requests require review before merging:

1. **Code quality checks** must pass (linting, formatting)
2. **Manual review** by maintainers
3. **Discussion** of any needed changes
4. **Approval** and merge

**What we look for in reviews:**

- Code quality and style
- Documentation completeness
- Backward compatibility
- Performance impact

Development Workflow
--------------------

**Branch Naming:**

- ``feature/feature-name`` - New features
- ``bugfix/issue-description`` - Bug fixes
- ``docs/topic`` - Documentation updates
- ``refactor/component-name`` - Code refactoring

**Commit Messages:**

Use clear, descriptive commit messages:

.. code-block:: text

    Add autocomplete support for icon widgets

    - Implement AJAX search functionality
    - Add keyboard navigation support
    - Update documentation

    Closes #123

**Version Bumping:**

- Follow semantic versioning
- Update version in ``__init__.py``
- Update changelog
- Tag releases appropriately

Documentation Contributions
---------------------------

**Areas needing documentation:**

- Usage examples
- Best practices
- Troubleshooting guides
- Performance tips
- Integration examples

**Documentation workflow:**

1. Edit ``.rst`` files in ``docs/``
2. Build locally: ``make html``
3. Check for errors and formatting
4. Submit pull request

**Writing guidelines:**

- Use clear, concise language
- Provide working code examples
- Include screenshots for UI features
- Cross-reference related sections

Release Process
---------------

**For maintainers:**

1. **Update version numbers** in:

   - ``django_remix_icon/__init__.py``
   - ``setup.py``
   - ``docs/conf.py``

2. **Update changelog:**

   - Move unreleased items to new version
   - Add release date
   - Create new unreleased section

3. **Create release:**

   .. code-block:: bash

       git tag v0.1.0
       git push origin v0.1.0
       python setup.py sdist bdist_wheel
       twine upload dist/*

4. **Update documentation** on ReadTheDocs

Getting Help
------------

**Communication channels:**

- GitHub Issues - Bug reports and feature requests
- GitHub Discussions - General questions and ideas
- Email - security@django-remix-icon.example.com (security issues)

**Before asking for help:**

- Check existing issues and documentation
- Provide minimal reproducible example
- Include relevant system information
- Be patient and respectful

Recognition
-----------

Contributors are recognized in:

- ``CONTRIBUTORS.md`` file
- Release notes for significant contributions
- GitHub contributor graphs

**Types of contributions we recognize:**

- Code contributions
- Documentation improvements
- Bug reports and issue reporting
- Community support
- Translations (if applicable)

License
-------

By contributing to Django RemixIcon, you agree that your contributions will be licensed under the same license as the project (MIT License).

Code of Conduct
---------------

This project follows the `Django Code of Conduct <https://www.djangoproject.com/conduct/>`_. All contributors are expected to uphold this code.

**In summary:**

- Be respectful and inclusive
- Welcome newcomers
- Be constructive in discussions
- Report unacceptable behavior

Questions?
----------

If you have questions about contributing:

- Open a GitHub Discussion
- Check existing issues and pull requests
- Read through this contributing guide
- Look at recent contributions for examples

Thank you for considering contributing to Django RemixIcon!
