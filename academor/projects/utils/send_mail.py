# from django.conf import settings
# from django.core.mail import EmailMessage


# def send_mail_func(user_email, custom_subject, custom_message, attachment_path=None, attachment_name=None):
#     email = EmailMessage(
#         subject=custom_subject,
#         body=custom_message,
#         from_email=settings.EMAIL_HOST_USER,
#         to=[user_email],
#     )

#     if attachment_path:
#         email.attach_file(attachment_path, mimetype=None)  

#     email.send(fail_silently=False)
