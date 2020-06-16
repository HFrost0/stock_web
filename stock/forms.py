from django import forms


class TimeForm(forms.Form):
    start_point = forms.DateTimeField(label='开始时间', widget=forms.DateInput(attrs={'type': 'date'}))
    end_point = forms.DateTimeField(label='结束时间', widget=forms.DateInput(attrs={'type': 'date'}))
