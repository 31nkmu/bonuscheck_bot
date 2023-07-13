from django.contrib import admin

from applications.checks.models import Check, Product, CodeWord, Gtin, Bonus


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "products", "product_count", "bonus_balance", "is_processed", "is_accepted", "is_reject")
    list_filter = ("owner",)

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
    list_display = ("price", "name", "quantity", "checks", "code")
    list_filter = ("check_field",)

    def checks(self, obj):
        return obj.check_field.id

    checks.short_description = 'id чека'


admin.site.register(CodeWord)
admin.site.register(Gtin)
admin.site.register(Bonus)
