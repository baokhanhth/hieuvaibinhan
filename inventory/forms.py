from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "cost_price",
            "profit_margin",
            "stock_quantity",
            "minimum_stock",
            "status",
        ]

        labels = {
            "name": "Mặt hàng",
            "cost_price": "Giá vốn",
            "profit_margin": "% Lợi nhuận mong muốn",
            "stock_quantity": "Số lượng nhập (m)",
            "minimum_stock": "Tồn kho tối thiểu",
            "status": "Trạng thái",
        }

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "autocomplete": "off",
                "id": "id_name",
            }),
            "cost_price": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",  
                "autocomplete": "off",
                "id": "id_cost_price",
            }),
            "profit_margin": forms.NumberInput(attrs={"class": "form-control",
                                                "id": "id_profit_margin",
                                                "readonly": True,
            }
        ),
            "stock_quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01",  
                "autocomplete": "off",
                "id": "id_stock_quantity",
            }),
            "minimum_stock": forms.NumberInput(attrs={ "class": "form-control",
                                                        "id": "id_minimum_stock",
                                                        "readonly": True,
                                                    }
                                                ),
            "status": forms.Select(attrs={
                "class": "form-select",
                "autocomplete": "off",
                "id": "id_status",
            }),
        }