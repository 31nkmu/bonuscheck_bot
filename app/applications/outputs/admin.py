from django.contrib import admin

from applications.outputs.models import Output, MinBalance


@admin.register(Output)
class OutputAdmin(admin.ModelAdmin):
    list_display = ("owner", "user", "amount", "status", "created_at")
    list_filter = ("status", "owner")

    def user(self, obj):
        if obj.owner.username:
            return obj.owner.username
        return obj.owner

    user.short_description = 'username'


admin.site.register(MinBalance)
