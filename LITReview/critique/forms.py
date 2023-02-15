from django import forms
from .models import Review, Ticket


class ReviewForm(forms.ModelForm):
    headline = forms.CharField(label="Titre", max_length=128, widget=forms.TextInput())
    rating = forms.ChoiceField(
        initial=1,
        label="Notes",
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
        choices=(
            (1, "1 étoile"),
            (2, "2 étoiles"),
            (3, "3 étoiles"),
            (4, "4 étoiles"),
            (5, "5 étoiles"),
        ),
    )
    body = forms.CharField(
        label="Critique", max_length=8192, widget=forms.Textarea(), required=False
    )

    class Meta:
        model = Review
        fields = ["headline", "rating", "body"]


class TicketForm(forms.ModelForm):
    title = forms.CharField(label="Titre", max_length=128, widget=forms.TextInput())
    description = forms.CharField(
        label="Description", max_length=2048, widget=forms.Textarea(), required=False
    )
    image = forms.ImageField(label="Image", required=False)

    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]
