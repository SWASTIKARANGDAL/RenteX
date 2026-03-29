from django import forms
from django.forms import inlineformset_factory
from .models import Product, ProductImage, ProductSpecification, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'description', 'brand', 'model_number',
            'condition', 'price_per_day', 'price_per_week', 'price_per_month',
            'deposit_amount', 'city', 'state', 'pincode', 'is_available'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary', 'alt_text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs['class'] = 'form-control'


ProductImageFormSet = inlineformset_factory(
    Product, ProductImage,
    form=ProductImageForm,
    extra=3, max_num=10, can_delete=True
)


class ProductSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search electronics...', 'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label='All Categories', widget=forms.Select(attrs={'class': 'form-select'}))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}))
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min price'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max price'}))
    condition = forms.ChoiceField(choices=[('', 'Any Condition')] + Product.CONDITION_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    sort = forms.ChoiceField(choices=[
        ('-created_at', 'Newest First'),
        ('price_per_day', 'Price: Low to High'),
        ('-price_per_day', 'Price: High to Low'),
        ('-views_count', 'Most Popular'),
    ], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
