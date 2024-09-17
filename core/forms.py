from django import forms


class LocationSearchForm(forms.Form):
    rank = forms.CharField(max_length=30, required=False)
    shelf = forms.CharField(max_length=30, required=False)
    tray = forms.CharField(max_length=30, required=False)
