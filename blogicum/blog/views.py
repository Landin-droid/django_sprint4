from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from blog.models import Post, Category


def index(request):
    template_name = "blog/index.html"
    post_list = Post.objects.all().filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category__is_published=True
    )[:5]

    context = {"post_list": post_list}
    return render(request, template_name, context)


def post_detail(request, id):
    template_name = "blog/detail.html"
    post = get_object_or_404(
        Post.objects.select_related('category').filter(
            id=id,
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True
        )
    )
    context = {"post": post}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = "blog/category.html"

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    category_posts_list = Post.objects.select_related(
        'author', 'location', 'category'
    ).filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category=category
    )
    context = {"category": category, "post_list": category_posts_list}
    return render(request, template_name, context)
