from django import forms
from .models import Pet

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            'name', 'image', 
            'age_years', 'age_months', 'weight',
            'species', 'breed', 'health_features'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 sm:text-sm transition duration-150 ease-in-out',
                                           'placeholder': 'Кличка вашого улюбленця'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'age_years': forms.NumberInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 sm:text-sm transition duration-150 ease-in-out',
                                                  'placeholder': 'Повних років', 'min': '0'}),
            'age_months': forms.NumberInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 sm:text-sm transition duration-150 ease-in-out',
                                                   'placeholder': 'Місяців (0-11)', 'min': '0', 'max': '11'}),
            'weight': forms.NumberInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 sm:text-sm transition duration-150 ease-in-out',
                                               'placeholder': 'Наприклад: 5.25', 'step': '0.01', 'min': '0.01'}),
            'species': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 sm:text-sm transition duration-150 ease-in-out',
                                              'placeholder': 'Наприклад: Собака, Кіт'}),
            'breed': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 sm:text-sm transition duration-150 ease-in-out',
                                            'placeholder': 'Наприклад: Такса, Сіамський (необов\'язково)'}),
            'health_features': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 sm:text-sm transition duration-150 ease-in-out',
                                                     'rows': 3,
                                                     'placeholder': 'Алергії, особливості характеру, улюблені іграшки тощо (необов\'язково)'}),
        }
        labels = {
            'name': 'Кличка улюбленця',
            'image': 'Фото (необов\'язково)',
            'age_years': 'Вік (повних років)',
            'age_months': 'Додатково місяців',
            'weight': 'Вага, кг (необов\'язково)',
            'species': 'Вид тварини',
            'breed': 'Порода (необов\'язково)',
            'health_features': 'Особливості здоров\'я та характеру (необов\'язково)',
        }
        help_texts = {
            'age_years': 'Вкажіть кількість повних років.',
            'age_months': 'Якщо вік менше року, вкажіть кількість місяців (0-11).',
            'weight': 'Вкажіть вагу в кілограмах (наприклад, 0.5 для 500г, або 5.25 для 5кг 250г).',
        }

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and weight <= 0:
            raise forms.ValidationError("Вага має бути позитивним числом.")
        return weight

    def clean(self):
        cleaned_data = super().clean()
        age_years = cleaned_data.get('age_years')
        age_months = cleaned_data.get('age_months')

        if age_years is not None and age_years < 0:
            self.add_error('age_years', "Кількість років не може бути від'ємною.")
        
        if age_months is not None and not (0 <= age_months <= 11):
            self.add_error('age_months', "Кількість місяців має бути від 0 до 11.")

        return cleaned_data