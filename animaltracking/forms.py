
from django import forms 
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"maxlength": 20})
        }


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ["name", "gender", "age", "color", "description", "image", "species", "tag"]
        widgets = {
            "description": forms.Textarea(attrs={"rows":5, "cols":100}),
            "image": forms.FileInput(attrs={"class":"hidden","accept":"image/*","onchange":"previewImage(event)", "required": "required"}),
            "tag": forms.CheckboxSelectMultiple(),
        }
     
     
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        description = cleaned_data.get("description")
        if len(description) > 200:
            raise ValidationError("คำอธิบายต้องไม่เกิน 200 ตัวอักษร")
        return cleaned_data
    

class StrayAnimalForm(forms.ModelForm):
    date_found = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    class Meta:
        model = StrayAnimal
        fields = ["animal", "date_found", "description_location", "latitude", "longitude"]
        widgets = {
            "latitude": forms.TextInput(attrs={"required": "required", "id": "id_latitude"}),
            "longitude": forms.TextInput(attrs={"required": "required", "id": "id_longitude"}),
            "description_location": forms.Textarea(attrs={"rows": 5, "cols": 100}),
        }
    def clean(self):
        cleaned_data = super().clean()
        description_location = cleaned_data.get("description_location")
        if len(description_location) > 200:
            raise ValidationError("คำอธิบายสถานที่ต้องไม่เกิน 200 ตัวอักษร")
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment_text"]

    def clean(self):
        cleaned_data = super().clean()
        comment_text = cleaned_data.get("comment_text")
        if len(comment_text) > 200:
            raise ValidationError("ความคิดเห็นต้องไม่เกิน 200 ตัวอักษร")
        return cleaned_data

class LostAnimalForm(forms.ModelForm):
    date_lost = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    class Meta:
        model = LostAnimal
        fields = ["animal", "date_lost", "description_location", "latitude", "longitude", "status"]
        widgets = {
            "latitude": forms.TextInput(attrs={"readonly": "readonly", "id": "id_latitude"}),
            "longitude": forms.TextInput(attrs={"readonly": "readonly", "id": "id_longitude"}),
            "description_location": forms.Textarea(attrs={"rows": 5, "cols": 100})
        }
    def clean(self):
        cleaned_data = super().clean()
        description_location = cleaned_data.get("description_location")
        if len(description_location) > 200:
            raise ValidationError("คำอธิบายสถานที่ต้องไม่เกิน 200 ตัวอักษร")
        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone_number"]
        widgets = {
            "phone_number": forms.TextInput(attrs={"maxlength": 10, "pattern": "[0-9]{10}"})
        }


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

        
