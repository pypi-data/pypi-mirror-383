=======================
django-contact-us-tools
=======================

A Django app to facilitate website 'contact us' functionality.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add ``"contact_us_tools"`` to your ``INSTALLED_APPS`` setting:

    .. code:: python

        INSTALLED_APPS = [
            # ...,
            "contact_us_tools",
        ]

2. Set up the necessary settings for sending emails. For example, if gmail is your chosen host:

    .. code:: python

        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST = 'smtp.gmail.com'
        EMAIL_USE_TLS = True
        EMAIL_PORT = 587
        EMAIL_HOST_USER = "example@gmail.com"
        EMAIL_HOST_PASSWORD = "exmample"

    See the django documentation https://docs.djangoproject.com/en/5.2/topics/email/#email-backends

3. Extend the ``BaseMessage`` model and set the ``BUSINESS_NAME`` and ``COPYRIGHT_YEAR`` attributes:
    
    .. code:: python
        
        from contact_us_tools.models import AbstractBaseMessage

        class Message(AbstractBaseMessage):
            BUSINESS_NAME = "My Business Name"
            COPYRIGHT_YEAR = 2025
    
    ``BUSINESS_NAME`` is your business or website name to be displayed in the automatic-reply email and ``COPYRIGHT_YEAR`` is the year to be displayed with the copyright notice in the email.

    For further configuration of the ``BaseMessage`` model, consult the docs https://django-contact-us-tools.readthedocs.io/en/latest/index.html.

4. Register the new model to your admit site:

    .. code:: python
    
            from django.contrib import admin
            admin.site.register(Message)

5. Create a new form or extend ``BaseContactUsForm`` and add the ``model`` attribute to the ``Meta`` class:

    .. code:: python

      from contact_us_tools.forms import BaseContactUsForm

      class ContactUsForm(BaseContactUsForm):
         class Meta(BaseContactUsForm.Meta):
            model = Message

6. Create a html template for the 'contact us' form. For example:

    .. code:: html

        <form action="" method="POST">
            {% csrf_token %}

            <legend>Contact Us</legend>
            <small>Got any questions? Fill out this form to reach out.</small>

            {{ form }}

            <button type="submit">Submit</button>
        </form>

7. Extend ``BaseContactUsView``, making sure to overwrite ``form_class`` and ``template_name`` with the form and html template you just created, as well as supplying a success url: 

    .. code:: python

        from django.urls import reverse
        from contact_us_tools.views import BaseContactUsView

        class ContactUsView(BaseContactUsView):
            form_class = ContactUsForm
            template_name = 'template_name'
            
            def get_success_url(self):
                return reverse('success_url_name')

    For further configuration of ``BaseContactUsView``, consult the docs https://django-contact-us-tools.readthedocs.io/en/latest/index.html.

8. Add a URL pattern to handle the rendering of the form:

    .. code:: python
        
        urlpatterns = [
            # ...,
            path('contact-us', ContactUsView.as_view(), name='contact-us'),
        ]

9. Run ``python manage.py makemigrations`` then ``python manage.py migrate`` to create the models.

10. Start the development server and visit the relevant url to test the 'contact us' form.

11. Visit the admin site to view the resulting addition to the relevant database table.