from django.contrib import admin

from applications.users.models import Users, Code, Check, Output, CodeWord, Product, Gtin

admin.site.register(CodeWord)
admin.site.register(Gtin)


def set_field_to_false(modeladmin, request, queryset):
    # Обновить поле на False для выбранных объектов
    queryset.update(is_active=False)


def set_field_to_true(modeladmin, request, queryset):
    queryset.update(is_active=True)


def ban_users(modeladmin, request, queryset):
    queryset.update(is_banned=True)


def unban_users(modeladmin, request, queryset):
    queryset.update(is_banned=False)


set_field_to_false.short_description = "Деактивировать коды"
set_field_to_true.short_description = "Активировать коды"
ban_users.short_description = "Забанить пользователей"
unban_users.short_description = "Разбанить пользователей"


@admin.register(Users)
class UserAdmin(admin.ModelAdmin):
    list_display = ("tg_id", "bonus_balance", "code", "checks", "registered_at")
    list_filter = ("code", "is_admin")
    actions = [ban_users, unban_users]

    def checks(self, obj):
        return len(obj.checks.all())

    checks.short_description = 'Чеки'


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ("qr_data", "owner", "products", "product_count")
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


@admin.register(Output)
class OutputAdmin(admin.ModelAdmin):
    list_display = ("owner", "amount", "status", "created_at")
    list_filter = ("status", "owner")


@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    actions = [set_field_to_false, set_field_to_true]
    list_display = ("keycode", "is_active")
