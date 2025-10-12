from .models import send_email_arg_names
from django.contrib import messages
from django.views.generic import FormView
    
class BaseContactUsView(FormView):
    send_email_kwargs = {}
    success_message = 'Your form has been successfully submitted. We will be in contact with you as soon as we can.'
    disp_success_msg = False

    def send_email(self, form):
        """Send an automatic-reply email to user."""
        # Check that the keys in the send_email_kwargs attribute are valid.
        if len(self.send_email_kwargs) > 0:
            for keyword in self.send_email_kwargs.keys():
                if keyword not in send_email_arg_names:
                    raise ValueError("Invalid keyword entered for send_email_kwargs attribute of {}. Check documentation for AbstractBaseMessage.send_email for valid keywords.".format(self.__class__.__name__))
        # Send the email
        form.save()
        form.instance.send_email(**self.send_email_kwargs)

    def form_valid(self, form):
        self.send_email(form)
        if self.disp_success_msg:
            messages.success(self.request, self.success_message)
        return super().form_valid(form)