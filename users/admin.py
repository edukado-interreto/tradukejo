from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DeeplAuthKey
from traduko.deepl import update_deepl_usage


@admin.register(DeeplAuthKey)
class DeeplAuthKeyAdmin(admin.ModelAdmin):
    exclude = ["user"]
    list_display = ["__str__", "name", "character_count", "used", "user", "created_on"]

    @admin.display()
    def used(self, obj):
        ratio = obj.character_count / obj.character_limit
        return f"{ratio * 100:0.2f}%"

    def save_model(self, request, obj, form, change):
        if change:
            update_deepl_usage(obj)
        else:
            obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(User, UserAdmin)
