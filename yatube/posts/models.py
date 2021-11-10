from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    """
    Класс Group

    Parameters
    ----------
    text : CharField
        Название группы
    slug : SlugField
        Адрес группы
    description : TextField
        Описание группы
    """
    title = models.CharField('Имя', max_length=200)
    slug = models.SlugField('Адрес', unique=True)
    description = models.TextField('Описание', blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(models.Model):
    """
    Класс Post

    Parameters
    ----------
    text : TextField
        Заголовок названия записи
    pub_date : DateTimeField
        текст "date published" это заголовок поля в интерфейсе администратора.
        auto_now_add говорит, что при создании новой записи
        автоматически будет подставлено текущее время и дата
    author : ForeignKey
        ссылка на модель User
    group : ForeignKey
        ссылка на primary_key таблицы Group
    """
    text = models.TextField('Название')
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
         """
         выводим текст поста
         """
         return self.text

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
