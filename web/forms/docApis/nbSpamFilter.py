from django import forms

class SpamCheckForm(forms.Form):
    """used to validate the spam to check"""
    spamToCheck=forms.CharField(
        max_length=1000,
        required=True,
    )

