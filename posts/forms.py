from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """
    Форма публикации постов на сайте
    """
    class Meta:
        model = Post
        fields = ('text', 'image', 'group')


class CommentForm(forms.ModelForm):
    """
    Форма комментирования постов на сайте
    """
    class Meta:
        model = Comment
        fields = ('text',)

    text = forms.CharField(widget=forms.Textarea)
