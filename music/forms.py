# django imports
from django import forms

# third party imports
from db_file_storage.form_widgets import DBClearableFileInput

# project imports
from music.models import CD


class CDForm(forms.ModelForm):
    class Meta:
        model = CD
        widgets = {
            'disc': DBClearableFileInput,
            'cover': DBClearableFileInput,
        }
