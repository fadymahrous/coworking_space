from django.forms import ModelForm
from .models import Categorization,TofaProductsRepository

class Categorization_Form(ModelForm):
    class Meta:
        model=Categorization
        fields=["main_category","sub_category","exposure"]
        
class TofaProductsRepository_form(ModelForm):
    class Meta:
        model=TofaProductsRepository
        fields=['item_name','category','brand','item_description','price','item_quantity']