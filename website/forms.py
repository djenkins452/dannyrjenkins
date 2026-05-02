from django import forms


class ContactForm(forms.Form):
    """Contact form for /connect/. Not backed by a model — submissions are
    emailed only, never stored."""

    EXECUTIVE_CONVERSATION = 'executive_conversation'
    ROLE_DISCUSSION = 'role_discussion'
    ADVISORY_SPEAKING = 'advisory_speaking'
    RESUME = 'resume'
    INQUIRY_CHOICES = [
        (EXECUTIVE_CONVERSATION, 'Executive conversation'),
        (ROLE_DISCUSSION, 'Role discussion'),
        (ADVISORY_SPEAKING, 'Advisory / speaking'),
        (RESUME, 'Resume request'),
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
