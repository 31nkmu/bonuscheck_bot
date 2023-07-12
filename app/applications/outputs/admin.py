from django.contrib import admin

from applications.outputs.models import Output, MinBalance


@admin.register(Output)
class OutputAdmin(admin.ModelAdmin):
    list_display = ("owner", "amount", "status", "created_at")
    list_filter = ("status", "owner")


admin.site.register(MinBalance)
