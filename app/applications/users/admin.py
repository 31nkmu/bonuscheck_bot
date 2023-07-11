from django.contrib import admin

from applications.users.models import Users, Code, Check, Output, CodeWord, Product, Gtin

admin.site.register(Output)
admin.site.register(CodeWord)
admin.site.register(Gtin)


def set_field_to_false(modeladmin, request, queryset):
    # Обновить поле на False для выбранных объектов
    queryset.update(is_active=False)


def ban_users(modeladmin, request, queryset):
    queryset.update(is_banned=True)


set_field_to_false.short_description = "Деактивировать коды"
ban_users.short_description = "Забанить пользователей"


class MyModelAdmin(admin.ModelAdmin):
    actions = [set_field_to_false]


@admin.register(Users)
class UserAdmin(admin.ModelAdmin):
    list_display = ("tg_id", "bonus_balance", "code", "checks")
    actions = [ban_users]

    def checks(self, obj):
        return len(obj.checks.all())


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ("qr_data", "owner", "products")

    def products(self, obj):
        return '\n'.join([i.name for i in obj.products.all()])


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("price", "name", "quantity", "check_field")


admin.site.register(Code, MyModelAdmin)
