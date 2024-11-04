from django.contrib import admin
from blog.models import Tag, Category, Page, Post
from django_summernote.admin import SummernoteModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe

# Register your models here.
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'slug',
    list_display_links = 'name',
    search_fields = 'id', 'name', 'slug',
    list_per_page = 10
    ordering = '-id',
    prepopulated_fields = {
        "slug": ('name',),
    }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'slug',
    list_display_links = 'name',
    search_fields = 'id', 'name', 'slug',
    list_per_page = 10
    ordering = '-id',
    prepopulated_fields = {
        "slug": ('name',),
    }

@admin.register(Page)
class PageAdmin(SummernoteModelAdmin):
    list_display = 'id', 'title', 'slug',
    list_display_links = 'title',
    search_fields = 'id', 'title', 'slug',
    list_per_page = 10
    ordering = '-id',
    prepopulated_fields = {
        "slug": ('title',),
    }
    summernote_fields = ('content',)

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    list_display = 'id', 'title', 'is_published', 'created_by',
    list_display_links = 'title',
    search_fields = 'id', 'title', 'excert', 'content',
    list_per_page = 50
    list_filter = 'category', 'is_published',
    list_editable = 'is_published',
    ordering = '-id',
    readonly_fields = ('created_at', 'updated_at', 'updated_by', 
                       'created_by','link')
    prepopulated_fields = {
        "slug": ('title',) ,
    }
    autocomplete_fields = 'tags', 'category'
    summernote_fields = ('content',)

    def link(self,obj):
        if not obj.pk:
            return '-'
        url_do_post = reverse('blog:post', args=(obj.slug,))
        safe_link = mark_safe(
            f'<a target="_blank" href="{url_do_post}">Ver Post</a>'
        )
        return safe_link

    def save_model(self, request, obj, form,change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user    
        obj.save()