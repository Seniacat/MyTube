from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'date_of_birth',
        'city',
        'avatar'
    )
    list_editable = ('city', 'avatar')
    search_fields = ('city', 'date_of_birth')
    empty_value_display = '-пусто-'


admin.site.register(Profile, ProfileAdmin)
