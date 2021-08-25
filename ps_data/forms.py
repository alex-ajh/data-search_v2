from django.forms.widgets import Widget
import re
from django import forms
from django.core.exceptions import ValidationError

class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Removes : as label suffix
        self.fields['keyword'].widget.attrs['style'] = 'width:600px; height:30px;'

    keyword = forms.CharField(max_length=100)

    # def clean_encoding_data(self): 
    #     data = self.cleaned_data['encoding_data'] 
    #     reg = re.compile('[0-9a-fA-F]{10}') 
    #     reg_result = reg.match(data) 
    #     if reg_result is None: 
    #         raise ValidationError("Input Data Error: Use only A~F, 0~9 with 10 digits")            
    #     return data

