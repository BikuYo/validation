from django import forms
# from .models import ValidationType, Mapping, Result

# class ValidationTypeForm(forms.ModelForm):
#     class Meta:
#         model = ValidationType
#         fields = ['name']

# class MappingForm(forms.ModelForm):
#     class Meta:
#         model = Mapping
#         fields = ['description']

# class ResultForm(forms.ModelForm):
#     class Meta:
#         model = Result
#         fields = ['validation_type', 'mapping', 'result']



class SQLQueryForm(forms.Form):
    sql_query = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter your SQL query here'
        }),
        label="SQL Query",
        max_length=5000
    )

    join_type = forms.ChoiceField(
        choices=[
            ('NO_CHANGE', 'CURRENT'),
            ('INNER JOIN', 'INNER JOIN'),
            ('LEFT JOIN', 'LEFT JOIN'),
            ('RIGHT JOIN', 'RIGHT JOIN'),
            ('FULL OUTER JOIN', 'FULL OUTER JOIN'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Join Type"
    )




class SQLValidationForm(forms.Form):
    source_sql = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter SQL query for Source Table'
            }),
        label="Source SQL Query",
    )
    target_sql = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter SQL query for Target Table'
            }),
        label="Target SQL Query",
    )
