from django import forms
from app.requests.models import ClientBeneficiary
  

class ImageForm(forms.ModelForm):
    class Meta:
        model = ClientBeneficiary
        fields = ['photo']
        labels = {
		'display_picture':('Upload Picture'),
		}
