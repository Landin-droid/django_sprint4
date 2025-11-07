from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class PublishCreateModel(models.Model):
    is_published = (models.
                    BooleanField(default=True,
                                 verbose_name='Опубликовано',
                                 help_text='Снимите галочку, '
                                           'чтобы скрыть публикацию.'))
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено')

    class Meta:
        abstract = True


class Category(PublishCreateModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(unique=True, verbose_name='Идентификатор',
                            help_text='Идентификатор страницы для URL; '
                                      'разрешены символы латиницы, цифры, '
                                      'дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishCreateModel):
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishCreateModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = (models.
                DateTimeField(verbose_name='Дата и время публикации',
                              help_text='Если установить дату и время'
                                        ' в будущем — можно делать'
                                        ' отложенные публикации.'))
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 verbose_name='Местоположение')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, verbose_name='Категория')
    image = models.ImageField(blank=True,
                              verbose_name='Фото',
                              upload_to='posts_images')
    @property
    def comment_count(self):
        return self.comments.count()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(PublishCreateModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    text = models.TextField(
        max_length=1000,
        verbose_name='Текст комментария'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Комментарий {self.author} к {self.post}'
