from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow


def index(request):
    """
    Главная страница сайта с выводом опубликованных записей
    """
    keyword = request.GET.get("q")
    posts = Post.objects.select_related('author', 'group').order_by(
        "-pub_date"
    )
    if keyword:
        posts = posts.filter(text__contains=keyword)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page, "keyword": keyword})


def group(request, slug):
    """
    функция для вывода страницы группы

    Note:
        функция get_object_or_404 получает по заданным критериям объект из
        базы данных или возвращает сообщение об ошибке, если объект не найден

        Метод .filter позволяет ограничить поиск по критериям. Это аналог
        добавления условия WHERE group_id = {group_id}
    """
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    """
    Представление обработки формы новой записи
    """
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            post.save()
            return redirect('index')
    return render(request, 'post_form.html', {'form': form, 'is_edit': False})


def profile(request, username):
    """Профиль пользователя"""
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.select_related(
        'author'
    ).filter(author=profile).order_by("-pub_date")
    if request.user.is_authenticated:
        following = profile.following.filter(user=request.user).exists()
    else:
        following = False
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html', {
        'profile': profile, 'following': following, 'page': page
    })


def post_view(request, username, post_id):
    """Просмотр записи пользователя"""
    user_profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user_profile)
    comments = Comment.objects.select_related(
        'author', 'post'
    ).filter(post__id=post_id).order_by("-created")
    form = CommentForm()

    return render(request, 'post.html', {
        'profile': user_profile,
        'post': post,
        'comments': comments,
        'form': form,
    })


@login_required
def post_edit(request, username, post_id):
    """Редактирование записи пользователя"""
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)

    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(
                'post', username=request.user.username, post_id=post_id
            )
    return render(
        request, 'post_form.html', {
            'form': form, 'post': post, 'is_edit': True
        },
    )


@login_required
def add_comment(request, username, post_id):
    """
    Добавляем написанный комментарий на сайт
    Parameters
    ----------
    username: Автор которому пишут комментарий
    post_id: id поста автора

    Returns
    -------
    Перенаправляет на исходную страницу
    """
    if request.method == 'POST':
        author_post = get_object_or_404(User, username=username)
        post = get_object_or_404(Post, pk=post_id, author=author_post)
        form = CommentForm(request.POST or None)
        if form.is_valid():
            user_comment = form.save(commit=False)
            user_comment.author = request.user
            user_comment.post = post
            user_comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    """
    Страница сайта с выводом записей избранными авторами
    """
    posts = Post.objects.filter(
        author__following__user=request.user
    ).order_by("-pub_date")

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    """
    Функция подписки на автора только для авторизированных пользователей
    """
    if request.user.username == username:
        # Проверка подписки на самого себя
        return redirect('profile', username=username)
    author_post = get_object_or_404(User, username=username)

    Follow.objects.get_or_create(user=request.user, author=author_post)

    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    """
    Функция отписки от автора только для авторизированных пользователей
    """
    if request.user.username == username:
        """Проверка отподписки на самого себя"""
        return redirect('profile', username=username)
    author_post = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author_post).delete()

    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
