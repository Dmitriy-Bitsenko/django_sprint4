from django.contrib import admin

from blog.models import Category, Location, Post, Comment


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'is_published',
        'created_at',
        'category'
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('is_published',)
    list_display_links = ('title',)


@admin.register(Location)
class FindLocation(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name__endswith']


class FindComment(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'created_at',)
    search_fields = ['text']


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, FindComment)
