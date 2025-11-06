from django import forms
from django.contrib.auth.models import User
from .models import Category, Location, Post, Comment


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Имя пользователя',
            'email': 'Email адрес',
        }
        help_texts = {
            'username': 'Обязательное поле. Только буквы, цифры и @/./+/-/_',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
      model = Category
      fields = '__all__'


class LocationForm(forms.ModelForm):
    class Meta:
      model = Location
      fields = '__all__'


class PostForm(forms.ModelForm):
    class Meta:
      model = Post
      fields = ['title', 'text', 'pub_date', 'location', 'category', 'image']

      widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                },
                format='%Y-%m-%dT%H:%M'
            )
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pub_date:
            self.initial['pub_date'] = self.instance.pub_date.strftime('%Y-%m-%dT%H:%M')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите ваш комментарий...'
            }),
        }
        labels = {
            'text': 'Текст комментария'
        }

class CommentUpdateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
        }
        labels = {
            'text': 'Редактировать комментарий'
        }
