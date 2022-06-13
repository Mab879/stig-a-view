from django import forms

from stig_a_view.base import models as base_models


class ImportStigUrlForm(forms.Form):
    product = forms.ModelChoiceField(queryset=base_models.Product.objects.all())
    version = forms.IntegerField(min_value=0)
    release = forms.IntegerField(min_value=0)
    release_date = forms.DateField()
    url = forms.URLField()
