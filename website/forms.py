from django import forms


class ContactForm(forms.Form):
    """Contact form for /connect/. Not backed by a model — submissions are
    emailed only, never stored."""

    CONVERSATION = 'conversation'
    RESUME = 'resume'
    INQUIRY_CHOICES = [
        (CONVERSATION, 'Conversation'),
        (RESUME, 'Resume Request'),
    ]

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'autocomplete': 'name'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    inquiry_type = forms.ChoiceField(
        choices=INQUIRY_CHOICES,
        label='Reason for reaching out',
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 5}),
    )

    def inquiry_display(self) -> str:
        return dict(self.INQUIRY_CHOICES).get(
            self.cleaned_data.get('inquiry_type', ''),
            '',
        )
