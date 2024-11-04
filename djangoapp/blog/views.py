from typing import Any
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from blog.models import Post, Page
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic import ListView, DetailView

posts = list(range(1000))


PER_PAGE = 9

class PostListView(ListView):

    model = Post
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'
    ordering = '-pk',
    paginate_by = PER_PAGE
    queryset = Post.objects.get_published()

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {'page_title': 'Home - '}
        )

        return context

class PageDetailView(DetailView):
    model = Page
    queryset = Page.objects.filter(is_published=True)
    context_object_name = 'page'
    slug_field = 'slug'
    template_name = 'blog/pages/page.html'
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(slug=self.kwargs.get('slug'))
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        page = self.get_object()
        page_title = f'{page.title} - Page -'
        context.update({
            'page_title': page_title
        })
        return context

class PostDetailView(DetailView):
    model = Post
    queryset = Post.objects.get_published()
    context_object_name = 'post'
    slug_field = 'slug'
    template_name = 'blog/pages/post.html'
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(slug=self.kwargs.get('slug'))
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        post_title = f'{post.title} - Post -'
        context.update({
            'page_title': post_title
        })
        return context

class CreatedByListView(PostListView):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._temp_context = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user:User = self._temp_context['user']

        if user is None:
            raise Http404()
        
        if (user.first_name):
            user_full_name = f'{user.first_name} {user.last_name}'
        else:
            user_full_name = user.username

        page_title = f'Posts de {user_full_name} - '

        context.update(
            {
                'page_title': page_title
            }
        )

        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(created_by__pk=self._temp_context['author_id'])
        return qs
    
    def get(self, request: HttpRequest, *args, **kwargs):

        author_id = self.kwargs.get('author_id', '')
        user = User.objects.filter(pk=author_id).first()
        if user is None:
            return redirect('blog:index')
        
        self._temp_context.update(
            {
                'author_id': author_id,
                'user': user,
            }
        )

        return super().get(request, *args, **kwargs)

class CategoryListView(PostListView):
    allow_empty = False
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        category = self.object_list
        page_title = f'{category[0].category.name} - Categoria - '
        context_data.update(
            {
                'page_title': page_title,
            }
        )
        return context_data
    def get_queryset(self):
        return super().get_queryset().filter(
            category__slug=self.kwargs.get('slug')
        )

class TagListView(PostListView):
    allow_empty = False
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        tags = self.object_list
        page_title = f'{tags[0].tags.first().name} - Tag - '
        context_data.update(
            {
                'page_title': page_title,
            }
        )
        return context_data
    def get_queryset(self):
        return super().get_queryset().filter(
            tags__slug=self.kwargs.get('slug')
        )  

class SearchListView(PostListView):
    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        self._search_value = request.GET.get('search', '').strip()
        return super().setup(request, *args, **kwargs)
    def get_queryset(self) -> QuerySet[Any]:
        search_value = self._search_value
        queryset =  super().get_queryset().filter(
            Q(title__icontains=search_value) |
            Q(excert__icontains=search_value) |
            Q(content__icontains=search_value)
            )
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_value = self._search_value
        page_title = f'{search_value[:30]} - Search - '
        context.update({
            'page_title': page_title,
            'search_value': search_value,
        })
        return context
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not self._search_value:
            return redirect('blog:index')
        return super().get(request, *args, **kwargs)
