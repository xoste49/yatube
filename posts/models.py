from django.contrib.auth import get_user_model
from django.db import models

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
    title = models.CharField(
        'Имя', max_length=200, help_text='Максимальная длина 200 символов'
    )
    slug = models.SlugField('Адрес', unique=True)
    description = models.TextField(
        'Описание', blank=True, null=True, help_text='Описание группы'
    )

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
        Текст записи
    pub_date : DateTimeField
        текст "date published" это заголовок поля в интерфейсе администратора.
        auto_now_add говорит, что при создании новой записи
        автоматически будет подставлено текущее время и дата
    author : ForeignKey
        ссылка на модель User
    group : ForeignKey
        ссылка на primary_key таблицы Group
    """
    text = models.TextField('Текст записи', help_text='Введите текст записи')
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="posts", verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, blank=True, null=True,
        verbose_name='Группа', help_text='Группа для записи'
    )
    image = models.ImageField(
        upload_to='posts/', blank=True, null=True, verbose_name='Изображение'
    )

    def __str__(self):
        """
        выводим текст поста
        """
        return self.text[:15]

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"


class Comment(models.Model):
    """
    система комментирования записей.
    На странице просмотра записи под текстом поста

    post — ссылка на пост, к которому оставлен комментарий
    (для связи модели Post с комментариями используйте имя comments ).
    author — ссылка на автора комментария
    (для связи модели User с комментариями используйте имя comments).
    text — текст комментария.
    created — автоматически подставляемые дата и время публикации комментария.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name='Автор'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    """
    user — ссылка на объект пользователя, который подписывается.
    Укажите имя связи: related_name="follower"

    author — ссылка на объект пользователя, на которого подписываются,
    имя связи пусть будет related_name="following"
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
