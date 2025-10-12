from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
import warnings

send_email_arg_names = [
    "text_file",
    "html_file",
    "from_email",
    "disp_cpr_notice",
    "disp_pp_notice",
    "disp_review_link",
    "copyright_year",
    "business_name",
    "review_link",
    "subject",
    "salutation",
    "main_content",
    "main_content_fbk",
    "closing",
    "signature",
]


class AbstractBaseMessage(models.Model):
    """An abstract base class to function as the foundation for "message" models."""

    TICKET_NUM_LENGTH = 4
    TEXT_FILE = "contact_us_tools/email.txt"
    HTML_FILE = "contact_us_tools/email.html"

    DISP_PRIVACY_POLICY_NOTICE = True
    DISP_COPYRIGHT_NOTICE = True
    DISP_REVIEW_LINK = False

    BUSINESS_NAME = None
    COPYRIGHT_YEAR = None
    REVIEW_LINK = None

    SUBJECT = "Message Received"
    SALUTATION = None
    MAIN_CONTENT = None
    MAIN_CONTENT_FBK = "Thank you very much for your feedback. It is much appreciated."
    CLOSING = None
    SIGNATURE = None

    class Type(models.TextChoices):
        ENQUIRY = 'ENQUIRY', 'Enquiry'
        FEEDBACK = 'FEEDBACK', 'Feedback'
        OTHER = 'OTHER', 'Other/Misc'

    type = models.CharField("type", max_length=8, choices=Type.choices)
    name = models.CharField(max_length=50, help_text="Name of sender")
    email = models.EmailField(max_length=50, help_text="Email address of sender")
    message = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)

    @property
    def ticket_number(self):
        """
        A ticket number which is the model's pk expressed a number whose number of digits is
        specified by TICKET_NUM_LENGTH.
        """
        if not self.pk:
            warnings.warn(f"The {self.__class__.__name__} object with a pk of {self.pk} does not exist.")
            return "".zfill(self.TICKET_NUM_LENGTH)
        return str(self.pk).zfill(self.TICKET_NUM_LENGTH)

    def get_email_context(self,
                          disp_cpr_notice=None,
                          disp_pp_notice=None,
                          disp_review_link=None,
                          copyright_year=None,
                          business_name=None,
                          review_link=None,
                          salutation=None,
                          main_content=None,
                          main_content_fbk=None,
                          closing=None,
                          signature=None,
                          ):
        """
        (dict) Returns the context to be used when rendering the email template.
        For details on the input parameters, see docs for the send_email method.

        Overwrite this method for custom context. If you're only adding to the available
        context and not replacing all of it with your own, make sure to call super() like so:

            def get_email_context(self, **kwargs):
                context = super().get_email_context(**kwargs)
                extra_context = {...}
                context.update(extra_context)
                return context
        """
        # Make sure the disp_cpr_notice variable is properly set
        if not disp_cpr_notice:
            disp_cpr_notice = self.DISP_COPYRIGHT_NOTICE

        # Make sure the disp_pp_notice variable is properly set
        if not disp_pp_notice:
            disp_pp_notice = self.DISP_PRIVACY_POLICY_NOTICE

        # Make sure the disp_review_link variable is properly set
        if not disp_review_link:
            disp_review_link = self.DISP_REVIEW_LINK

        # Make sure the copyright_year variable is properly set
        if not copyright_year:
            copyright_year = self.COPYRIGHT_YEAR

        # Make sure the business_name variable is properly set
        if not business_name:
            business_name = self.BUSINESS_NAME

        # Make sure the review_link variable is properly set
        if not review_link:
            review_link = self.REVIEW_LINK

        # Make sure the salutation variable is properly set
        if not salutation:
            if not self.SALUTATION:
                salutation = f"Dear {self.name}"
            else:
                salutation = self.SALUTATION

        # Indicates if the user has overwritten the MAIN_CONTENT attribute or
        # provided an input for the main_content variable.
        is_main_content_provided = False

        # Make sure the main_content_fbk variable is properly set
        if not main_content_fbk:
            main_content_fbk = self.MAIN_CONTENT_FBK

        # Make sure the main_content variable is properly set
        if not main_content:
            main_content = self.MAIN_CONTENT
            if self.MAIN_CONTENT:
                is_main_content_provided = True
        else:
            is_main_content_provided = True

        # Make sure the closing variable is properly set
        if not closing:
            if not self.CLOSING:
                closing = "Kind regards"
            else:
                closing = self.CLOSING

        # Make sure the signature variable is properly set
        if not signature:
            if not self.SIGNATURE:
                signature = business_name
            else:
                signature = self.SIGNATURE

        # Raise an error if business_name is None
        if business_name is None:
            raise ValueError(
                "No value provided for business_name. " \
                "Either provide an input value for business_name or provide a value for " \
                "the {}.BUSINESS_NAME attribute.".format(
                    self.__class__.__name__
                )
            )

        # Raise an error if disp_cpr_notice is True while copyright_year is None
        if copyright_year is None and disp_cpr_notice == True:
            raise ValueError(
                "disp_cpr_notice is True but no value provided for copyright_year. " \
                "Either provide an input value for copyright_year or provide a " \
                "value for the {cls}.COPYRIGHT_YEAR attribute, or either input False " \
                "for disp_cpr_year or set the {cls}.DISP_COPYRIGHT_NOTICE attribute to False.".format(
                    cls=self.__class__.__name__
                )
            )

        # Raise an error if disp_review_link is True while review_link is None
        if review_link is None and disp_review_link == True:
            raise ValueError(
                "disp_review_link is True but no value provided for review_link. " \
                "Either provide an input value for review_link or provide a value " \
                "for the {cls}.REVIEW_LINK attribute, or either input False for " \
                "disp_review_link or set the {cls}.DISP_REVIEW_LINK attribute to False.".format(
                    cls=self.__class__.__name__
                )
            )

        # Create and return the context
        context = {
            'ticket_number': self.ticket_number,
            'name': self.name,
            'message': self.message,
            'date_created': self.date_created,
            'disp_pp_notice': disp_pp_notice,
            'disp_cpr_notice': disp_cpr_notice,
            'disp_review_link': disp_review_link,
            'copyright_year': copyright_year,
            'business_name': business_name,
            'review_link': review_link,
            'salutation': salutation,
            'main_content': main_content,
            'main_content_fbk': main_content_fbk,
            'closing': closing,
            'signature': signature,
            'is_feedback': self.is_feedback(),
            'is_main_content_provided': is_main_content_provided,
        }

        return context

    def send_email(self, text_file=None, html_file=None, from_email=None, subject=None, **kwargs):
        """
        Send an automatic-reply email to the user notifying them that their enquiry has been received.

        Parameters:
            text_file (string or None): Directory of the text version of the email template.
                If None, use TEXT_FILE class attribute.

            html_file (string or None): Directory of the hmtl version of the email template.
                If None, use HTML_FILE class attribute.

            *NOTE: If using custom values for text_file or html_file, the django.template.loader.render_to_string
            function might prove useful.

            from_email (string or None): Sender's email address. If None, try using EMAIL_HOST_USER setting.

            subject (string or None): Email's subject line. If None, use SUBJECT class attribute which is by
                default "Message Received".

        kwargs options:

            disp_cpr_notice (bool or None): Indicates if copyright notice should be displayed on the email.
                Notice is of the form: "<copyright symbol><copyright_year>, <business_name>" if html_file is used.
                                   Or: "copyright <copyright_year>, <business_name>" if text_file is used.
                If None, use DISP_COPYRIGHT_NOTICE class attribute.

            disp_pp_notice (bool or None): Indicates if a privacy policy notice should be displayed in email.
                Notice is of the form: "This email has been sent in accordance with the <business_name> Privacy Policy".
                If None, use DISP_PRIVACY_POLICY_NOTICE class attribute.

            disp_review_link (bool or None): Indicates if link to submit a review should be displayed in email.
                Link displayed like so: "We would love to hear your feedback. Please leave us a review at <review_link>."
                If None, use DISP_REVIEW_LINK class attribute.

            copyright_year (int or None): Year to be displayed in email's copyright notice.
                If None, use COPYRIGHT_YEAR class attribute.

            business_name (string or None): Name of business or website to display in the email.
                If None, use BUSINESS_NAME class attribute.

            review_link (str or None): Link where use can submit a review.
                If None, use REVIEW_LINK class attribute.

            salutation (string or None): Email's salutation or greeting. If None, use SALUTATION class attribute. But if
                SALUTATION is None, set to string of the form: "Dear <self.name>".

            main_content (string or None): Email's main content or body. i.e., the content between the salutation and closing.
                If None and MAIN_CONTENT class attribute is also None, do nothing. Content in text_file or html_file will be used.
                Otherwise, use MAIN_CONTENT.

            main_content_fbk (string or None): Email's main content or body; like main_content, but only if the message type is FEEDBACK.

            closing (string or None): Email's closing line (without the comma). If None and CLOSING class attribute is None, use "Kind regards".
                Other wise, use CLOSING.

            signature (string or None): Email's signature. If None and SIGNATURE class attribute is None, use business_name. Otherwise, use SIGNATURE.
        """
        # Raise error if the model has not been created and saved
        if not self.pk:
            raise self.DoesNotExist(
                "The {} object does not exist. Save the object to the database first, and then try sending the email.".format(
                    self.__class__.__name__))

        # Make sure the text_file variable is properly set
        if not text_file:
            text_file = self.TEXT_FILE

        # Make sure the html_file variable is properly set
        if not html_file:
            html_file = self.HTML_FILE

        # Make sure the from_email variable is properly set
        if not from_email:
            try:
                from_email = settings.EMAIL_HOST_USER
            except:
                raise ValueError("Set the EMAIL_HOST_USER setting or input a value for from_email.")

        # Make sure the subject variable is properly set
        if not subject:
            subject = self.SUBJECT

        # Get email context
        context = self.get_email_context(**kwargs)
        context.update({"from_email": from_email})

        # Create the body text for the email
        text_content = render_to_string(text_file, context)
        html_content = render_to_string(html_file, context)

        # Create and send the email message
        msg = mail.EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[self.email],
        )

        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def is_feedback(self):
        """(bool) Return True if the message type is FEEDBACK. False otherwise."""
        if self.type == self.Type.FEEDBACK:
            return True
        return False

    class Meta:
        abstract = True


class AbstractBaseMessageExt(AbstractBaseMessage):
    """
    An extended version of AbstractBaseMessage with added fields and models to allow for ability to mark
    the matter of the message as being closed/resolved or open/unresolved.
    """
    is_closed = models.BooleanField(default=False)
    date_closed = models.DateTimeField(blank=True, null=True)
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)

    def mark_closed(self, closed_by):
        """Close the enquiry."""
        self.is_closed = True
        self.date_closed = timezone.now()
        self.closed_by = closed_by

    def reopen(self):
        """Reopen the enquiry."""
        self.is_closed = False
        self.date_closed = None
        self.closed_by = None

    class Meta:
        abstract = True
