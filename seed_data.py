import os
import random
from decimal import Decimal
from datetime import datetime, timedelta

import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "fabric_store.settings",
)

django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import Notification
from inventory.models import (
    Product,
    ProductPriceHistory,
    PurchaseReceipt,
    PurchaseItem,
)
from sales.models import (
    SalesOrder,
    SalesOrderItem,
)

User = get_user_model()

########################################################################
# CẤU HÌNH
########################################################################

PASSWORD = "Demo@123"

START_DATE = datetime(2026, 6, 1)
END_DATE = datetime(2026, 7, 31)

PROFIT_MARGIN = Decimal("30.00")
MINIMUM_STOCK = Decimal("5.00")

########################################################################
# NHÂN VIÊN
########################################################################

EMPLOYEES = [

    {
        "username": "nv01",
        "full_name": "Nguyễn Văn An",
        "phone": "0901111111",
    },

    {
        "username": "nv02",
        "full_name": "Trần Thị Bình",
        "phone": "0902222222",
    },

]

########################################################################
# NHÀ CUNG CẤP
########################################################################

SUPPLIERS = [

    ("Kho Vải Bình An", "0905111111"),

    ("Công ty Dệt Hòa Thọ", "0905222222"),

    ("Kho Vải Việt Phát", "0905333333"),

    ("Công ty Dệt Thành Công", "0905444444"),

    ("Kho Vải Minh Tâm", "0905555555"),

]

########################################################################
# DANH SÁCH MẶT HÀNG
########################################################################

PRODUCTS = [

    ("Vải Kate Mỹ", 38000),
    ("Vải Kate Silk", 42000),
    ("Vải Kate Ford", 40000),

    ("Vải Cotton 100%", 65000),
    ("Vải Cotton 65/35", 56000),

    ("Vải Linen Hàn", 98000),
    ("Vải Linen Nhật", 110000),
    ("Vải Linen Trắng", 92000),

    ("Vải Kaki Thành Công", 72000),
    ("Vải Kaki Cotton", 68000),

    ("Vải Jeans Xanh", 125000),
    ("Vải Jeans Đen", 128000),

    ("Vải Canvas", 84000),
    ("Vải Oxford", 76000),

    ("Vải Bamboo", 82000),
    ("Vải Rayon", 62000),
    ("Vải Modal", 73000),

    ("Vải Mango", 64000),

    ("Vải Satin", 70000),

    ("Vải Gấm", 98000),

    ("Vải Voan Hoa", 47000),
    ("Vải Voan Trơn", 45000),

    ("Vải Organza", 60000),

    ("Vải Ren Hoa", 68000),
    ("Vải Ren Lưới", 63000),

    ("Vải Đũi", 72000),
    ("Vải Đũi Thái", 76000),

    ("Vải Lụa Ý", 130000),
    ("Vải Lụa Hàn", 98000),

    ("Vải Thun Cotton 2 Chiều", 55000),
    ("Vải Thun Cotton 4 Chiều", 68000),
    ("Vải Thun Cá Sấu", 63000),

    ("Vải Bố", 47000),

    ("Vải Tơ", 120000),

    ("Vải Muslin", 52000),

]

########################################################################
# HÀM TIỆN ÍCH
########################################################################

def random_datetime_in_day(day):

    return datetime(

        day.year,
        day.month,
        day.day,

        random.randint(8, 19),
        random.randint(0, 59),
        random.randint(0, 59),

    )


def choose_employee(users):

    return random.choice(users)


def choose_discount():

    return random.choice(

        [

            Decimal("0"),
            Decimal("0"),
            Decimal("0"),

            Decimal("10000"),
            Decimal("20000"),
            Decimal("50000"),

        ]

    )


def initial_quantity(product_name):

    hot_products = [

        "Vải Kate Mỹ",
        "Vải Kate Silk",
        "Vải Kate Ford",

        "Vải Cotton 100%",
        "Vải Cotton 65/35",

        "Vải Linen Hàn",
        "Vải Linen Nhật",
        "Vải Linen Trắng",

        "Vải Kaki Thành Công",

        "Vải Jeans Xanh",

    ]

    medium_products = [

        "Vải Kaki Cotton",

        "Vải Canvas",
        "Vải Oxford",

        "Vải Bamboo",
        "Vải Rayon",
        "Vải Modal",

        "Vải Mango",

        "Vải Satin",

        "Vải Đũi",
        "Vải Đũi Thái",

        "Vải Thun Cotton 2 Chiều",
        "Vải Thun Cotton 4 Chiều",
        "Vải Thun Cá Sấu",

    ]

    if product_name in hot_products:

        return Decimal(random.randint(350, 550))

    if product_name in medium_products:

        return Decimal(random.randint(180, 300))

    return Decimal(random.randint(60, 120))

########################################################################
# XÓA DỮ LIỆU
########################################################################

def clear_data():

    print("Đang xóa dữ liệu cũ...")

    Notification.objects.all().delete()

    SalesOrderItem.objects.all().delete()
    SalesOrder.objects.all().delete()

    PurchaseItem.objects.all().delete()
    PurchaseReceipt.objects.all().delete()

    ProductPriceHistory.objects.all().delete()
    Product.objects.all().delete()

    User.objects.filter(
        role=User.Role.EMPLOYEE,
    ).delete()

    print("✔ Đã xóa dữ liệu.")


########################################################################
# TẠO NHÂN VIÊN
########################################################################

def create_users():

    print("Đang tạo nhân viên...")

    users = []

    created_time = timezone.make_aware(
        datetime(2026, 6, 1, 8, 0, 0)
    )

    for employee in EMPLOYEES:

        user = User.objects.create(

            username=employee["username"],

            full_name=employee["full_name"],

            phone=employee["phone"],

            role=User.Role.EMPLOYEE,

            is_active=True,

        )

        user.set_password(PASSWORD)

        user.save(update_fields=["password"])

        User.objects.filter(
            pk=user.pk,
        ).update(

            created_at=created_time,

            updated_at=created_time,

        )

        user.refresh_from_db()

        users.append(user)

    print(f"✔ Đã tạo {len(users)} nhân viên.")

    return users


########################################################################
# TẠO MẶT HÀNG
########################################################################

def create_products():

    print("Đang tạo mặt hàng...")

    products = []

    created_time = timezone.make_aware(
        datetime(2026, 6, 1, 8, 0, 0)
    )

    for name, cost_price in PRODUCTS:

        product = Product.objects.create(

            name=name,

            cost_price=Decimal(str(cost_price)),

            profit_margin=PROFIT_MARGIN,

            stock_quantity=Decimal("0.00"),

            minimum_stock=MINIMUM_STOCK,

            status=Product.Status.ACTIVE,

        )

        Product.objects.filter(
            pk=product.pk,
        ).update(

            created_at=created_time,

            updated_at=created_time,

        )

        product.refresh_from_db()

        products.append(product)

    print(f"✔ Đã tạo {len(products)} mặt hàng.")

    return products

########################################################################
# TẠO PHIẾU NHẬP ĐẦU KỲ
########################################################################

def create_first_purchase(users):

    print("Đang tạo phiếu nhập đầu kỳ...")

    receipt = PurchaseReceipt.objects.create(

        employee=users[0],

        supplier_name="Kho Vải Bình An",

        supplier_phone="0905111111",

    )

    created_time = timezone.make_aware(
        datetime(2026, 6, 1, 8, 0, 0)
    )

    total = Decimal("0")

    for product in Product.objects.all():

        quantity = initial_quantity(product.name)

        item = PurchaseItem.objects.create(

            receipt=receipt,

            product=product,

            quantity=quantity,

            unit_price=product.cost_price,

        )

        total += item.subtotal

        product.stock_quantity += quantity

        product.save(update_fields=["stock_quantity"])

    PurchaseReceipt.objects.filter(
        pk=receipt.pk
    ).update(

        created_at=created_time,

        updated_at=created_time,

        total_amount=total,

    )

    receipt.refresh_from_db()

    print("✔ Đã tạo phiếu nhập đầu kỳ.")

    return receipt


########################################################################
# TẠO THÔNG BÁO
########################################################################

def create_notification(product, created_time):

    users = User.objects.filter(

        role=User.Role.EMPLOYEE,

        is_active=True,

    )

    for user in users:

        existed = Notification.objects.filter(

            receiver=user,

            product=product,

            type=Notification.Type.LOW_STOCK,

            is_resolved=False,

        ).exists()

        if existed:
            continue

        notification = Notification.objects.create(

            receiver=user,

            product=product,

            type=Notification.Type.LOW_STOCK,

            title="Sắp hết hàng",

            message=f"Sắp hết loại vải '{product.name}'. Vui lòng nhập thêm mặt hàng!",

        )

        Notification.objects.filter(
            pk=notification.pk
        ).update(

            created_at=timezone.make_aware(created_time),

        )
        
########################################################################
# TẠO HÓA ĐƠN
########################################################################

def create_sale_order(employee, created_time):

    order = SalesOrder.objects.create(

        employee=employee,

        status=SalesOrder.Status.COMPLETED,

    )

    aware_time = timezone.make_aware(created_time)

    SalesOrder.objects.filter(
        pk=order.pk
    ).update(

        created_at=aware_time,

        completed_at=aware_time,

        updated_at=aware_time,

    )

    order.refresh_from_db()

    return order


########################################################################
# TẠO CHI TIẾT HÓA ĐƠN
########################################################################

def create_order_items(order, created_time):

    total = Decimal("0")

    available_products = list(

        Product.objects.filter(

            status=Product.Status.ACTIVE,

            stock_quantity__gt=Decimal("0.50"),

        )

    )

    random.shuffle(available_products)

    selected_products = available_products[: random.randint(2, 5)]

    if not selected_products:

        return None

    item_count = 0

    for product in selected_products:

        quantity = Decimal(

            str(

                round(

                    random.uniform(1, 8),

                    2,

                )

            )

        )

        if quantity > product.stock_quantity:

            quantity = product.stock_quantity

        if quantity <= 0:

            continue

        SalesOrderItem.objects.create(

            order=order,

            product=product,

            quantity=quantity,

            unit_price=product.selling_price,

        )

        total += quantity * product.selling_price

        item_count += 1

        product.stock_quantity -= quantity

        product.save(update_fields=["stock_quantity"])

        if product.stock_quantity <= product.minimum_stock:

            create_notification(

                product,

                created_time,

            )

    if item_count == 0:

        order.delete()

        return None

    return total


########################################################################
# TẠO DỮ LIỆU BÁN HÀNG
########################################################################

def generate_sales(users):

    print("Đang tạo hóa đơn bán...")

    current_day = START_DATE

    total_orders = 0

    while current_day <= END_DATE:

        orders_per_day = random.randint(3, 4)

        for _ in range(orders_per_day):

            employee = choose_employee(users)

            created_time = random_datetime_in_day(current_day)

            order = create_sale_order(

                employee,

                created_time,

            )

            total_amount = create_order_items(

                order,

                created_time,

            )

            if total_amount is None:

                continue

            discount = choose_discount()

            if discount > total_amount:

                discount = Decimal("0")

            SalesOrder.objects.filter(
                pk=order.pk
            ).update(

                total_amount=total_amount,

                discount=discount,

                final_amount=total_amount - discount,

            )

            total_orders += 1

        if current_day.day in [10, 20, 30]:

            create_restock_receipt(

                users,

                current_day,

            )

        current_day += timedelta(days=1)

    print(f"✔ Đã tạo {total_orders} hóa đơn.")
    
    
########################################################################
# TẠO PHIẾU NHẬP BỔ SUNG
########################################################################

def create_restock_receipt(users, current_day):

    low_products = Product.objects.filter(
        status=Product.Status.ACTIVE,
        stock_quantity__lte=10,
    )

    if not low_products.exists():
        return

    supplier = random.choice(SUPPLIERS)

    receipt = PurchaseReceipt.objects.create(
        employee=choose_employee(users),
        supplier_name=supplier[0],
        supplier_phone=supplier[1],
    )

    total = Decimal("0")

    for product in low_products:

        quantity = Decimal(random.randint(150, 350))

        item = PurchaseItem.objects.create(
            receipt=receipt,
            product=product,
            quantity=quantity,
            unit_price=product.cost_price,
        )

        total += item.subtotal

        product.stock_quantity += quantity
        product.save(update_fields=["stock_quantity"])

        Notification.objects.filter(
            product=product,
            is_resolved=False,
        ).update(
            is_resolved=True,
        )

    created_time = timezone.make_aware(
        random_datetime_in_day(current_day)
    )

    PurchaseReceipt.objects.filter(
        pk=receipt.pk
    ).update(
        created_at=created_time,
        updated_at=created_time,
        total_amount=total,
    )

    receipt.refresh_from_db()


########################################################################
# HÓA ĐƠN NHÁP
########################################################################

def create_draft_orders(users):

    print("Đang tạo hóa đơn nháp...")

    for _ in range(8):

        created_time = random_datetime_in_day(
            START_DATE + timedelta(
                days=random.randint(0, 60)
            )
        )

        order = SalesOrder.objects.create(
            employee=choose_employee(users),
            status=SalesOrder.Status.DRAFT,
        )

        aware_time = timezone.make_aware(created_time)

        SalesOrder.objects.filter(
            pk=order.pk
        ).update(
            created_at=aware_time,
            updated_at=aware_time,
        )

        total = Decimal("0")

        products = random.sample(
            list(Product.objects.filter(status=Product.Status.ACTIVE)),
            random.randint(2, 4),
        )

        for product in products:

            quantity = Decimal(
                str(round(random.uniform(1, 5), 2))
            )

            SalesOrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.selling_price,
            )

            total += quantity * product.selling_price

        SalesOrder.objects.filter(
            pk=order.pk
        ).update(
            total_amount=total,
            discount=Decimal("0"),
            final_amount=total,
        )

    print("✔ Đã tạo hóa đơn nháp.")


########################################################################
# HÓA ĐƠN ĐÃ HỦY
########################################################################

def create_cancelled_orders(users):

    print("Đang tạo hóa đơn đã hủy...")

    for _ in range(5):

        created_time = random_datetime_in_day(
            START_DATE + timedelta(
                days=random.randint(0, 60)
            )
        )

        order = SalesOrder.objects.create(
            employee=choose_employee(users),
            status=SalesOrder.Status.CANCELLED,
        )

        aware_time = timezone.make_aware(created_time)

        SalesOrder.objects.filter(
            pk=order.pk
        ).update(
            created_at=aware_time,
            completed_at=aware_time,
            updated_at=aware_time,
        )

        total = Decimal("0")

        products = random.sample(
            list(Product.objects.filter(status=Product.Status.ACTIVE)),
            random.randint(2, 4),
        )

        for product in products:

            quantity = Decimal(
                str(round(random.uniform(1, 4), 2))
            )

            SalesOrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.selling_price,
            )

            total += quantity * product.selling_price

        SalesOrder.objects.filter(
            pk=order.pk
        ).update(
            total_amount=total,
            discount=Decimal("0"),
            final_amount=total,
        )

    print("✔ Đã tạo hóa đơn đã hủy.")
    
    ########################################################################
# THỐNG KÊ
########################################################################

def print_summary():

    print("\n" + "=" * 60)
    print("SEED DATA THÀNH CÔNG")
    print("=" * 60)

    print(f"Nhân viên             : {User.objects.count()}")
    print(f"Mặt hàng              : {Product.objects.count()}")
    print(f"Lịch sử giá           : {ProductPriceHistory.objects.count()}")
    print(f"Phiếu nhập            : {PurchaseReceipt.objects.count()}")
    print(f"Chi tiết phiếu nhập   : {PurchaseItem.objects.count()}")
    print(f"Hóa đơn               : {SalesOrder.objects.count()}")
    print(f"Chi tiết hóa đơn      : {SalesOrderItem.objects.count()}")
    print(f"Thông báo             : {Notification.objects.count()}")

    print("=" * 60)

    print("\nTÀI KHOẢN")

    print("----------------------------------------")
    print("Username : nv01")
    print(f"Password : {PASSWORD}")
    print("----------------------------------------")

    print("Username : nv02")
    print(f"Password : {PASSWORD}")
    print("----------------------------------------")
    
    
########################################################################
# MAIN
########################################################################

def main():

    random.seed(2026)

    clear_data()

    users = create_users()

    create_products()

    create_first_purchase(users)

    generate_sales(users)

    create_draft_orders(users)

    create_cancelled_orders(users)

    print_summary()

    print("\nHoàn tất tạo dữ liệu mẫu.")


if __name__ == "__main__":

    main()