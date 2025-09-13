from django import forms
from django.contrib.auth.models import User, Group
from app.models import Election, Candidate, Party
from django.core.exceptions import ValidationError
from django.utils import timezone

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['name', 'description', 'start_date', 'end_date', 'active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter election name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter election description'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Election Name',
            'description': 'Description',
            'start_date': 'Start Date & Time',
            'end_date': 'End Date & Time',
            'active': 'Activate Election',
        }
        help_texts = {
            'active': 'Check this box to make the election visible to voters immediately. Uncheck to keep it as a draft.',
        }

    # Add custom field definitions to handle datetime-local format
    start_date = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'step': '60'  # 1 minute steps
        }, format='%Y-%m-%dT%H:%M'),
        help_text='Select both date and time for when voting starts'
    )
    
    end_date = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'step': '60'  # 1 minute steps
        }, format='%Y-%m-%dT%H:%M'),
        help_text='Select both date and time for when voting ends'
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date >= end_date:
                raise ValidationError("End date must be after start date.")
            
            # Allow elections to start within the next hour (more flexible)
            from django.utils import timezone
            from datetime import timedelta
            min_start_time = timezone.now() + timedelta(minutes=30)
            if start_date < min_start_time:
                raise ValidationError("Start date must be at least 30 minutes in the future to allow for setup.")

class CandidateFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        
        users = []
        for form in self.forms:
            if form.cleaned_data:
                user = form.cleaned_data.get('user')
                if user:
                    if user in users:
                        raise ValidationError("Each user can only be a candidate once per election.")
                    users.append(user)
        
        if len(users) < 2:
            raise ValidationError("An election must have at least 2 candidates.")

class CandidateForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(
            is_active=True,
            groups__name='Candidates'
        ).distinct(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select a candidate",
        help_text="Only users in the 'Candidates' group are shown"
    )
    party = forms.ModelChoiceField(
        queryset=Party.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="No Party (Independent)",
        required=False
    )
    symbol = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Upload candidate symbol (optional)",
        required=False
    )

    class Meta:
        model = Candidate
        fields = ['user', 'party', 'symbol']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if there are any candidates available and update help text
        candidate_users = User.objects.filter(
            is_active=True,
            groups__name='Candidates'
        ).distinct()
        
        if candidate_users.count() == 0:
            self.fields['user'].help_text = "⚠️ No candidates available. Create users and add them to 'Candidates' group first."