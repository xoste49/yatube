from django.contrib import admin
# из файла models импортируем модель Post
from .models import Post, Group


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Класс PostAdmin используется для работы с публикациями на сайте"""
    list_display = ("pk", "text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Класс GroupAdmin для работы с групами"""
    list_display = ("pk", "title", "description")
    empty_value_display = "-пусто-"
