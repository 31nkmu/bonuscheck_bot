from django.contrib import admin

from applications.users.models import Users, Code, Check, Output

admin.site.register(Users)
admin.site.register(Code)
admin.site.register(Check)
admin.site.register(Output)
