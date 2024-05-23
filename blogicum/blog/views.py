from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)

from core.mixins import CommentMixinView
from core.utils import (
    get_post_published_query,
    get_post_all_query,
    get_post_data
)
from blog.forms import CommentEditForm, UserEditForm, PostEditForm
from blog.models import Category, Post, Comment, User
from blogicum.settings import POST_COUNT


class CommentCreateWiew(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentEditForm
    template_name = 'blog/comment.html'


class MainPostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POST_COUNT

    def get_queryset(self):
        return get_post_published_query()


class CategoryPostListView(MainPostListView):
    template_name = 'blog/category.html'
    category = None

    def get_queryset(self):
        slug = self.kwargs.get('category_slug')
        self.category = get_object_or_404(
            Category, slug=slug, is_published=True
        )
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class UserPostsListView(MainPostListView):
    template_name = 'blog/profile.html'
    author = None

    def get_queryset(self):
        return Post.objects.filter(
            author__username=self.kwargs['username']
        ).select_related(
            'location', 'category', 'author'
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    post_data = None

    def get_queryset(self):
        self.post_data = get_object_or_404(Post, pk=self.kwargs['pk'])
        if self.post_data.author == self.request.user:
            return get_post_all_query().filter(pk=self.kwargs['pk'])
        return get_post_published_query().filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentEditForm()
        context['comments'] = self.object.comments.all().select_related(
            'author')
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostEditForm(instance=self.object)
        return context

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentEditForm
    template_name = 'blog/comment.html'
    post_data = None

    def dispatch(self, request, *args, **kwargs):
        self.post_data = get_post_data(self.kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_data
        if self.post_data.author != self.request.user:
            self.send_author_email()
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse('blog:post_detail', kwargs={'pk': pk})

    def send_author_email(self):
        post_url = self.request.build_absolute_uri(self.get_success_url())
        recipient_email = self.post_data.author.email
        subject = 'New comment'
        message = (
            f'Пользователь {self.request.user} добавил '
            f'комментарий к посту {self.post_data.title}.\n'
            f'Читать комментарий {post_url}'
        )
        send_mail(
            subject=subject,
            message=message,
            recipient_list=[recipient_email],
            fail_silently=True,
            from_email=None)


class CommentUpdateView(CommentMixinView, UpdateView):
    form_class = CommentEditForm


class CommentDeleteView(CommentMixinView, DeleteView):
    ...
