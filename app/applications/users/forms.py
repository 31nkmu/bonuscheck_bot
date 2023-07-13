from django import forms

from applications.users.models import Code


class CodeForm(forms.ModelForm):
    excel_file = forms.FileField(label='Excel файл')

    class Meta:
        model = Code
        fields = ['excel_file']
