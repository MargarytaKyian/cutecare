from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    requested_datetime = forms.DateTimeField(
        label="Бажана дата та час",
        help_text="Оберіть дату та час не раніше поточного моменту.",
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'mt-1 block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 sm:text-sm transition duration-150 ease-in-out',
            }
        )
    )
    notes = forms.CharField(
        label="Примітки (необов'язково)",
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'class': 'mt-1 block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 sm:text-sm transition duration-150 ease-in-out resize-none min-h-[10rem] max-h-[20rem] overflow-y-auto',
                'placeholder': 'Наприклад, вкажіть особливості вашого улюбленця або побажання щодо візиту...'
            }
        ),
        required=False
    )

    class Meta:
        model = Appointment
        fields = ['requested_datetime', 'notes']

    def clean_requested_datetime(self):
        datetime_val = self.cleaned_data.get('requested_datetime')
        
        if datetime_val:
            if datetime_val < timezone.now():
                raise ValidationError(
                    "Неможливо обрати минулу дату або час. Будь ласка, оберіть майбутній час.",
                    code='past_datetime'
                )
        return datetime_val