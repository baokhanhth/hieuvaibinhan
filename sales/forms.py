from decimal import Decimal
from django import forms
from inventory.models import Product
from .models import SalesOrder, SalesOrderItem

class OrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ["discount"]
        widgets = {
            "discount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "1000",
                }
            ),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = SalesOrderItem
        fields = ["quantity"]

        widgets = { "quantity": forms.NumberInput(
                    attrs={
                    "class": "quantity-input",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),
        }


class AddOrderItemForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.none(),empty_label="Chọn mặt hàng",)

    quantity = forms.DecimalField( min_value=Decimal("0.01"), decimal_places=2, max_digits=10, initial=1,
        widget=forms.NumberInput(
            attrs={ "class": "form-control",
                    "step": "0.01",}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.all().order_by("name")