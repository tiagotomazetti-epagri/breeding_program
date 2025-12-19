from django import forms
from .models import Location

class LocationAdminForm(forms.ModelForm):
    lat_degrees = forms.IntegerField(
        label="Graus (Lat)",
        required=False,
        min_value=0,
        max_value=90
    )
    lat_minutes = forms.IntegerField(
        label="Minutos (Lat)",
        required=False,
        min_value=0,
        max_value=59
    )
    lat_seconds = forms.FloatField(
        label="Segundos (Lat)",
        required=False,
        min_value=0,
        max_value=59.99
    )
    lat_direction = forms.ChoiceField(
        label="Direção (Lat)",
        choices=[('S', 'Sul'), ('N', 'Norte')],
        required=False
    )

    lon_degrees = forms.IntegerField(
        label="Graus (Lon)",
        required=False,
        min_value=0,
        max_value=180
    )
    lon_minutes = forms.IntegerField(
        label="Minutos (Lon)",
        required=False,
        min_value=0,
        max_value=59
    )
    lon_seconds = forms.FloatField(
        label="Segundos (Lon)",
        required=False,
        min_value=0,
        max_value=59.99
    )
    lon_direction = forms.ChoiceField(
        label="Direção (Lon)",
        choices=[('O', 'Oeste'), ('L', 'Leste')],
        required=False
    )

    class Meta:
        model = Location
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Sobrescreve o __init__ para preencher os campos DMS a partir dos
        valores decimais slavos no banco de dados quando o formulário é carregado.
        """
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.latitude is not None and instance.longitude is not None:
            lat_abs = abs(instance.latitude)
            self.initial['lat_degrees'] = int(lat_abs)
            self.initial['lat_minutes'] = int((lat_abs * 60) % 60)
            self.initial['lat_seconds'] = round((lat_abs * 3600) % 60, 2)
            self.initial['lat_direction'] = 'N' if instance.latitude >= 0 else 'S'

            lon_abs = abs(instance.longitude)
            self.initial['lon_degrees'] = int(lon_abs)
            self.initial['lon_minutes'] = int((lon_abs * 60) % 60)
            self.initial['lon_seconds'] = round((lon_abs * 3600) % 60, 2)
            self.initial['lon_direction'] = 'L' if instance.longitude >= 0 else 'O'
    
    def save(self, commit=True):
        """
        Sobrescreve o save() para converter os dados DMS para decimal
        antes de salvar a instância do modelo.
        """
        instance = super().save(commit=False)

        lat_d = self.cleaned_data.get('lat_degrees') or 0
        lat_m = self.cleaned_data.get('lat_minutes') or 0
        lat_s = self.cleaned_data.get('lat_seconds') or 0.0
        lat_dir = self.cleaned_data.get('lat_direction')

        lon_d = self.cleaned_data.get('lon_degrees') or 0
        lon_m = self.cleaned_data.get('lon_minutes') or 0
        lon_s = self.cleaned_data.get('lon_seconds') or 0.0
        lon_dir = self.cleaned_data.get('lon_direction')

        if lat_d or lat_m or lat_s:
            decimal_lat = float(lat_d) + float(lat_m)/60 + float(lat_s)/3600
            if lat_dir == 'S':
                decimal_lat = -decimal_lat
            instance.latitude = decimal_lat
        else:
            instance.latitude = None

        if lon_d or lon_m or lon_s:
            decimal_lon = float(lon_d) + float(lon_m)/60 + float(lon_s)/3600
            if lon_dir == 'O':
                decimal_lon = -decimal_lon
            instance.longitude = decimal_lon
        else:
            instance.longitude = None

        if commit:
            instance.save()
            
        return instance

class MutationCreationForm(forms.Form):
    new_name = forms.CharField(
        label="Novo Nome do Mutante",
        help_text="Ex: 'Gala Gui', 'Royal Gala'",
        max_length=255
    )
    mutant_character = forms.CharField(
        label="Caractere Mutante",
        help_text="Descreva a principal característica da mutação. Ex: 'Resistência a MFG', 'Maior coloração'",
        widget=forms.Textarea(attrs={'rows': 4})
    )