from django.contrib.auth.models import Permission
from django.contrib import admin
from guardian.admin import GuardedModelAdmin
# Register your models here.
from chat.models import Room, Message


class RoomAdmin(GuardedModelAdmin):
    pass
    # prepopulated_fields = {"slug": ("title",)}
    # list_display = ('title', 'slug', 'created_at')
    # search_fields = ('title', 'content')
    # ordering = ('-created_at',)
    # date_hierarchy = 'created_at'

admin.site.register(Room, GuardedModelAdmin)
admin.site.register(Permission)
admin.site.register(Message)