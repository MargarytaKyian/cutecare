from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    requested_datetime = forms.DateTimeField(
        label="Бажана дата та час",
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'mt-1 block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition duration-150 ease-in-out',
            }
        )
    )
    notes = forms.CharField(
        label="Примітки (необов'язково)",
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'class': 'mt-1 block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition duration-150 ease-in-out',
                'placeholder': 'Наприклад, вкажіть особливості вашого улюбленця або побажання щодо візиту...'
            }
        ),
        required=False
    )

    class Meta:
        model = Appointment
        fields = ['requested_datetime', 'notes']