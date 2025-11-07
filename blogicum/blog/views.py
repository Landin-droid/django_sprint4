from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Post, Category, Comment
from .forms import UserEditForm, PostForm, CommentForm, CommentUpdateForm
from django.core.paginator import Paginator
from django.http import Http404
from django.db import models


class UserDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user == self.object:
            user_posts = Post.objects.filter(author=self.object)
        else:
            user_posts = Post.objects.filter(
                author=self.object,
                is_published=True,
                pub_date__lte=timezone.now()
            ).filter(
                models.Q(category__is_published=True) |
                models.Q(category__isnull=True)
            )
        
        user_posts = user_posts.order_by('-pub_date')
        paginator = Paginator(user_posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['paginator'] = paginator
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'
    
    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostListView(ListView):
    model = Post
    ordering = '-pub_date'
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        queryset = Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(), 
        ).filter(
            models.Q(category__is_published=True) |
            models.Q(category__isnull=True)
        )
        
        return queryset.order_by('-pub_date')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})

    def handle_no_permission(self):
        """Обрабатываем случаи, когда пользователь не авторизован или не автор/админ"""
        if not self.request.user.is_authenticated:
            return redirect('blog:post_detail', pk=self.kwargs.get('pk'))
        else:
            return redirect('blog:post_detail', pk=self.kwargs.get('pk'))


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update['is_delete_page'] = True
        if 'form' in context:
            del context['form']
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        
        if not self.is_post_accessible(post):
            from django.http import Http404
            raise Http404("Публикация не найдена")
        return post

    def is_post_accessible(self, post):
        if post.author == self.request.user:
            return True

        if not post.is_published:
            return False
        
        if post.category and not post.category.is_published:
            return False
        
        if post.pub_date > timezone.now():
            return False
        
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_future_post'] = self.object.pub_date > timezone.now()
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author').order_by('created_at')
        return context


class CategoryPostsView(ListView):
    model = Category
    paginate_by = 10
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        
        queryset = Post.objects.select_related(
            'author', 'location', 'category'
        ).filter(
            category=self.category,
            is_published=True,
            pub_date__lte=timezone.now()
        )
        
        return queryset.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs['post_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        return context


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentUpdateForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_pk'],
            post__pk=self.kwargs['post_pk']
        )

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs['post_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        return context


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_pk'],
            post__pk=self.kwargs['post_pk']
        )

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs['post_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        if 'form' in context:
            del context['form']
        context['is_delete_page'] = True
        return context
