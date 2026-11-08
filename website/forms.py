from django import forms


class InquiryTypeField(forms.ChoiceField):
    """Offers only the current choices, but still accepts a legacy value.

    A visitor who loaded /connect/ before a deploy may submit one of the
    retired values. Rejecting it would lose their message, and mapping it to a
    new option would misstate what they chose, so it is accepted as-is and
    labelled as a legacy option in the notification.
    """

    def __init__(self, *, legacy_choices=(), **kwargs):
        self.legacy_choices = dict(legacy_choices)
        super().__init__(**kwargs)

    def valid_value(self, value):
        return super().valid_value(value) or str(value) in self.legacy_choices


class ContactForm(forms.Form):
    """Contact form for /connect/. Not backed by a model — submissions are
    emailed only, never stored."""

    PROFESSIONAL_NETWORKING = 'professional_networking'
    HR_WORKFORCE_TECHNOLOGY = 'hr_workforce_technology'
    SOFTWARE_AUTOMATION_AI = 'software_automation_ai'
    SPEAKING_KNOWLEDGE_SHARING = 'speaking_knowledge_sharing'
    OTHER = 'other'
    INQUIRY_CHOICES = [
        (PROFESSIONAL_NETWORKING, 'Professional networking'),
        (HR_WORKFORCE_TECHNOLOGY, 'HR and workforce technology'),
        (SOFTWARE_AUTOMATION_AI, 'Software, automation, and AI'),
        (SPEAKING_KNOWLEDGE_SHARING, 'Speaking or knowledge sharing'),
        (OTHER, 'Other'),
    ]

    # Retired Nov 2026. Never shown; accepted only from stale form pages and
    # reported under their original label, without reinterpretation.
    LEGACY_INQUIRY_CHOICES = [
        ('executive_conversation', 'Executive conversation'),
        ('role_discussion', 'Role discussion'),
        ('advisory_speaking', 'Advisory / speaking'),
        ('resume', 'Resume request'),
    ]

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'autocomplete': 'name'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    inquiry_type = InquiryTypeField(
        choices=INQUIRY_CHOICES,
        legacy_choices=LEGACY_INQUIRY_CHOICES,
        label='Reason for reaching out',
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 5}),
    )

    def inquiry_display(self) -> str:
        value = self.cleaned_data.get('inquiry_type', '')
        current = dict(self.INQUIRY_CHOICES)
        if value in current:
            return current[value]
        legacy = dict(self.LEGACY_INQUIRY_CHOICES)
        if value in legacy:
            return f'{legacy[value]} (legacy option)'
        return ''
