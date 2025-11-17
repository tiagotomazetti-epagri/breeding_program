from django import forms
from .models import GeneticMaterial

# class OriginSelectionForm(forms.Form):
#     ORIGIN_CHOICES = [
#         ('population', 'Gerado por uma população do programa (Híbrido)'),
#         ('external', 'Origem externa ou parental (Cultivar, Seleção)'),
#         ('mutation', 'Mutação de um material existente'),
#     ]

#     origin_type = forms.ChoiceField(
#         choices=ORIGIN_CHOICES,
#         label="Qual a origem do novo material genético?",
#         widget=forms.RadioSelect,
#         required=True
#     )


# class GeneticMaterialAdminForm(forms.ModelForm):
#     # 1. Aceitamos um novo argumento 'origin_type' no construtor
#     origin_type = forms.CharField(widget=forms.HiddenInput(), required=False)

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.origin_type = kwargs.pop('origin_type', None)

#         # Remove o link de "adicionar" dos widgets
#         for field_name in ['population', 'mother', 'father', 'mutated_from']:
#             if field_name in self.fields:
#                 self.fields[field_name].widget.can_add_related = False

#     def clean(self):
#         """
#         Garante que 'is_epagri_material' seja definido ANTES da validação do modelo.
#         """
#         cleaned_data = super().clean()

#         origin_type = cleaned_data.get('origin_type')

#         if origin_type == 'population':
#             cleaned_data['is_epagri_material'] = True
        
#         return cleaned_data

#     class Meta:
#         model = GeneticMaterial
#         fields = '__all__'
