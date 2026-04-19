
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Conge, Employe


class RegisterForm(UserCreationForm):
    """Formulaire d'inscription"""
    
    # Mot de passe secret pour devenir admin RH
    CODE_ADMIN_RH = "adminrh2025"
    
    # Champs supplémentaires pour l'employé
    matricule = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Matricule'
        })
    )
    nom = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    prenom = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    telephone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone (optionnel)'
        })
    )
    poste = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Poste'
        })
    )
    departement = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Département'
        })
    )
    date_embauche = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter les classes Bootstrap aux champs de mot de passe
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })
    
    def clean_email(self):
        """Vérifier que l'email n'existe pas déjà"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte avec cet email existe déjà.")
        return email
    
    def clean_matricule(self):
        """Vérifier que le matricule n'existe pas déjà"""
        matricule = self.cleaned_data.get('matricule')
        if Employe.objects.filter(matricule=matricule).exists():
            raise forms.ValidationError("Ce matricule est déjà utilisé.")
        return matricule
    
    def save(self, commit=True):
        # Créer l'utilisateur avec l'email comme username
        user = User()
        user.username = self.cleaned_data['email']  # Utiliser l'email comme username
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        
        # Déterminer le rôle en fonction du mot de passe
        password = self.cleaned_data['password1']
        role = 'admin_rh' if password == self.CODE_ADMIN_RH else 'employe'
        
        if commit:
            user.save()
            
            # Créer l'employé associé avec le rôle approprié
            Employe.objects.create(
                user=user,
                matricule=self.cleaned_data['matricule'],
                nom=self.cleaned_data['nom'],
                prenom=self.cleaned_data['prenom'],
                email=self.cleaned_data['email'],
                telephone=self.cleaned_data.get('telephone', ''),
                poste=self.cleaned_data['poste'],
                departement=self.cleaned_data['departement'],
                date_embauche=self.cleaned_data['date_embauche'],
                statut='actif',
                role=role  # Rôle déterminé automatiquement
            )
        
        return user


class LoginForm(forms.Form):
    """Formulaire de connexion avec email"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )



class CongeForm(forms.ModelForm):
    class Meta:
        model = Conge
        fields = ['type_conge', 'date_debut', 'date_fin', 'justificatif_texte', 'justificatif_fichier']
        
        widgets = {
            'type_conge': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'justificatif_texte': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Motif de la demande (optionnel)'
            }),
            'justificatif_fichier': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            })
        }
        
        labels = {
            'type_conge': 'Type de congé',
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
            'justificatif_texte': 'Motif',
            'justificatif_fichier': 'Pièce justificative (optionnel)'
        }