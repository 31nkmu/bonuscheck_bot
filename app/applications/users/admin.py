import pandas as pd
from django.contrib import admin
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path

from applications.users.forms import CodeForm
from applications.users.models import Users, Code
from config.settings import BACKEND_LOGGER as log


@admin.register(Users)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "tg_id", "bonus_balance", "code", "checks", "registered_at")
    list_filter = ("code", "is_admin")
    actions = ['ban_users', 'unban_users']

    def ban_users(self, request, queryset):
        queryset.update(is_banned=True)

    def unban_users(self, request, queryset):
        queryset.update(is_banned=False)

    def checks(self, obj):
        return len(obj.checks.all())

    checks.short_description = 'Чеки'
    ban_users.short_description = "Забанить пользователей"
    unban_users.short_description = "Разбанить пользователей"


@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    actions = ['set_field_to_false', 'set_field_to_true']
    list_display = ("keycode", "is_active")
    list_filter = ("is_active",)

    def set_field_to_false(self, request, queryset):
        # Обновить поле на False для выбранных объектов
        queryset.update(is_active=False)

    def set_field_to_true(self, request, queryset):
        queryset.update(is_active=True)

    set_field_to_false.short_description = "Деактивировать коды"
    set_field_to_true.short_description = "Активировать коды"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-codes/', self.import_codes_view, name='import-codes'),
            path('inactive_codes/', self.inactive_codes_view, name='inactive-codes')
        ]
        return custom_urls + urls

    def import_codes_view(self, request):
        if request.method == 'POST' and 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
            values = df.iloc[:, 0].tolist()
            for value in values:
                try:
                    code = Code(keycode=value, is_active=True)
                    code.save()
                except IntegrityError:
                    log.warning('Код уже существует')
                except Exception as err:
                    log.error(err)

            self.message_user(request, "Коды успешно загружены из файла Excel.")
            return HttpResponseRedirect('../')

        show_form = request.GET.get('show_form', False)
        form = CodeForm(request.POST or None, request.FILES or None)
        context = {
            'show_form': show_form,
            'form': form
        }
        return TemplateResponse(request, 'admin/import_codes.html', context)

    def inactive_codes_view(self, request):
        if request.method == 'POST' and 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
            values = df.iloc[:, 0].tolist()
            for value in values:
                try:
                    code = Code.objects.get(keycode=value, is_active=True)
                    code.is_active = False
                    code.save()
                except Exception as err:
                    log.warning(err)

            self.message_user(request, "Коды из файла Excel успешно деактивированы.")
            return HttpResponseRedirect('../')

        show_form = request.GET.get('show_form', False)
        form = CodeForm(request.POST or None, request.FILES or None)
        context = {
            'show_form': show_form,
            'form': form
        }
        return TemplateResponse(request, 'admin/inactive_codes.html', context)
