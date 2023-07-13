from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from applications.checks.models import Check, Product, CodeWord, Gtin, Bonus


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "products", "product_count", "bonus_balance", "is_processed", "is_accepted", "is_reject"
    )
    list_filter = ("owner", "is_processed", "is_accepted", "is_reject")

    def products(self, obj):
        return ' | '.join([i.name for i in obj.products.all()])

    def user(self, obj):
        if obj.owner.username:
            return obj.owner.username
        return obj.owner

    def product_count(self, obj):
        return len(obj.products.all())

    product_count.short_description = 'Количество продуктов'
    products.short_description = 'Продукты'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "quantity", "checks_link", "code")
    list_filter = ("check_field",)

    def checks_link(self, obj):
        check_id = obj.check_field.id
        url = reverse("admin:checks_check_change", args=[check_id])
        return format_html('<a href="{}">{}</a>', url, check_id)

    checks_link.short_description = "Чеки"
    checks_link.admin_order_field = "check_field"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("check_field")
        return queryset


admin.site.register(CodeWord)
admin.site.register(Gtin)
admin.site.register(Bonus)
