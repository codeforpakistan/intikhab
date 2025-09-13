from django import forms
from django.contrib.auth.models import User
from app.models import Election, Candidate, Party
from django.core.exceptions import ValidationError

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['name', 'description', 'start_date', 'end_date']
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
        }
        labels = {
            'name': 'Election Name',
            'description': 'Description',
            'start_date': 'Start Date & Time',
            'end_date': 'End Date & Time',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default values only for new elections (not when editing)
        if not self.instance.pk:
            from django.utils import timezone
            from datetime import datetime, time
            
            now = timezone.now()
            # Default start time: Tomorrow at 9:00 AM
            tomorrow = now.date() + timezone.timedelta(days=1)
            default_start = timezone.make_aware(datetime.combine(tomorrow, time(9, 0)))
            
            # Default end time: Same day at 5:00 PM
            default_end = timezone.make_aware(datetime.combine(tomorrow, time(17, 0)))
            
            # Set initial values for the fields
            self.fields['start_date'].initial = default_start.strftime('%Y-%m-%dT%H:%M')
            self.fields['end_date'].initial = default_end.strftime('%Y-%m-%dT%H:%M')

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


class ElectionUpdateForm(forms.ModelForm):
    """Form for updating elections - includes active field"""
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
        queryset=User.objects.none(),  # Will be set properly in __init__
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
        self.election = kwargs.pop('election', None)
        super().__init__(*args, **kwargs)
        
        # Filter out users who are already candidates in this election
        if self.election:
            # Get users who are already candidates in this election
            existing_candidate_users = Candidate.objects.filter(
                election=self.election
            ).values_list('user_id', flat=True)
            
            # Filter the queryset to exclude existing candidates
            available_users = User.objects.filter(
                is_active=True,
                groups__name='Candidates'
            ).exclude(id__in=existing_candidate_users).distinct()
            
            self.fields['user'].queryset = available_users
            
            if available_users.count() == 0:
                if existing_candidate_users:
                    self.fields['user'].help_text = "⚠️ All available candidates are already assigned to this election."
                else:
                    self.fields['user'].help_text = "⚠️ No candidates available. Create users and add them to 'Candidates' group first."
        else:
            # Fallback for when no election is provided
            candidate_users = User.objects.filter(
                is_active=True,
                groups__name='Candidates'
            ).distinct()
            
            if candidate_users.count() == 0:
                self.fields['user'].help_text = "⚠️ No candidates available. Create users and add them to 'Candidates' group first."

    def clean_user(self):
        """Validate that user is not already a candidate in this election"""
        user = self.cleaned_data.get('user')
        if user and hasattr(self, 'election'):
            # Check if this user is already a candidate in this election
            existing_candidate = Candidate.objects.filter(
                user=user, 
                election=self.election
            ).first()
            
            if existing_candidate:
                raise ValidationError(f"{user.get_full_name()} is already a candidate in this election.")
        
        return user