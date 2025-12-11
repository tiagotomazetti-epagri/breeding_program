from django import forms

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