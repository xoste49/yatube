from django.shortcuts import render, get_object_or_404

from .models import Post, Group

def index(request):
    keyword = request.GET.get("q", None)
    if keyword:
        posts = Post.objects.select_related('author').select_related(
            'group').filter(text__contains=keyword).all().order_by(
            "-pub_date")[:11]
        return render(
            request, "index.html", {"posts": posts, "keyword": keyword}
        )
    else:
        posts = Post.objects.order_by("-pub_date")[:11]
        return render(request, "index.html", {"posts": posts})
    #latest = Post.objects.order_by("-pub_date")[:11]



def group_posts(request, slug):
    """
    view-функция для страницы сообщества

    Note:
        функция get_object_or_404 получает по заданным критериям объект из
        базы данных или возвращает сообщение об ошибке, если объект не найден

        Метод .filter позволяет ограничить поиск по критериям. Это аналог
        добавления условия WHERE group_id = {group_id}
    """
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    return render(request, "group.html", {"group": group, "posts": posts})
