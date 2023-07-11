from django.contrib import admin

from applications.users.models import Users, Code, Check, Output, CodeWord, Product, Gtin

admin.site.register(Users)
admin.site.register(Code)
admin.site.register(Check)
admin.site.register(Output)
admin.site.register(CodeWord)
admin.site.register(Product)
admin.site.register(Gtin)
