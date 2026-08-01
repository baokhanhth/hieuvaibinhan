from django import template

register = template.Library()

@register.filter
def money(value):
    if value in [None, ""]:
        return ""

    try:
        # Ép kiểu dữ liệu về float trước khi định dạng
        numeric_value = float(value)
        return f"{numeric_value:,.0f}".replace(",", ".") + "đ"
    except (ValueError, TypeError):
        return value