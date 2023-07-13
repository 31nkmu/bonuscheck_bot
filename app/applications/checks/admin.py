from django.contrib import admin

from applications.checks.models import Check, Product, CodeWord, Gtin, Bonus


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ("qr_data", "owner", "products", "product_count", "bonus_balance")
    list_filter = ("owner",)

    def products(self, obj):
        return ' | '.join([i.name for i in obj.products.all()])

    products.short_description = 'Продукты'

    def product_count(self, obj):
        return len(obj.products.all())

    product_count.short_description = 'Количество продуктов'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("price", "name", "quantity", "check_field")
    list_filter = ("check_field",)


admin.site.register(CodeWord)
admin.site.register(Gtin)
admin.site.register(Bonus)
