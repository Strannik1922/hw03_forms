from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group")
        group = forms.ModelChoiceField(queryset=Post.objects.all(),
                                       required=False, to_field_name="group")
        widgets = {
            'text': forms.Textarea(),
        }

        labels = {
            "group": "Группа",
            "text": "Текст"
        }
