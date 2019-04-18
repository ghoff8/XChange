from django.contrib import admin

from .models import UserProfile, Asset, Bookmark

class AssetInline(admin.StackedInline):
    model = Asset
    extra = 0

class BookmarkInline(admin.StackedInline):
    model = Bookmark
    extra = 0

class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                  {'fields': ['user']}),
    ]
    
    inlines = [AssetInline, BookmarkInline]
admin.site.register(UserProfile, UserProfileAdmin)