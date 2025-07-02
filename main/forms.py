from django import forms
from .models import Category, Event, Participant

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = '__all__'
