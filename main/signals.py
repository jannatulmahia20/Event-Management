from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
#from .models import RSVP
from django.contrib.auth.models import User
from .views import send_activation_email 

@receiver(post_migrate)
def create_user_roles(sender, **kwargs):
    roles = ['Admin', 'Organizer', 'Participant']
    for role in roles:
        Group.objects.get_or_create(name=role)


# @receiver(post_save, sender=RSVP)
# def send_rsvp_notification(sender, instance, created, **kwargs):
#     if created:
#         participant_email = instance.participant.email  # adjust to your model
#         event_name = instance.event.name
#         send_mail(
#             subject=f'RSVP Confirmation for {event_name}',
#             message=f'Hi {instance.participant.name}, you have successfully RSVP’d for {event_name}.',
#             from_email='no-reply@youremail.com',
#             recipient_list=[participant_email],
#             fail_silently=False,
#         )



 

@receiver(post_save, sender=User)
def send_activation_on_create(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        
        send_activation_email(None, instance)  