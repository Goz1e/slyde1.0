from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


# class Date_input(forms.DateInput):
#     input_type= 'date'

     
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username',)


    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user        

class LoginForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username','password')
        widgets={
            "username": forms.TextInput(attrs={"class":'border-success border-opacity-25',}),
            "password":forms.PasswordInput(attrs={"class":'border-success border-opacity-25',}),
        }

    def clean(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            password = self.cleaned_data['password']

            if not authenticate(username=username,password=password):
                raise forms.ValidationError('invalid credentials')




# class UserChangeForm(forms.ModelForm):
#     """A form for updating users. Includes all the fields on
#     the user, but replaces the password field with admin's
#     disabled password hash display field.
#     """
#     password = ReadOnlyPasswordHashField()

#     class Meta:
#         model = User
#         fields = ('username', 'password', 'is_active', 'is_admin')



# class ProfileEditForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ('first_name', 'last_name','phone_number', 'date_of_birth')
#         widgets={
#             "date_of_birth": Date_input(attrs={"class":'border-success border-opacity-25',}),
#         }


# VIEW 
# from contextlib import redirect_stderr
# from django.shortcuts import render
# from django.contrib.auth import authenticate, login, logout
# import email
# from django.shortcuts import render, redirect
# from .forms import ProfileEditForm, UserCreationForm, LoginForm
# from .models import *
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages

# # Create your views here.

# def index(request):
#     if request.user.is_authenticated:
#         return redirect('task:dashboard')
    
#     template_name = 'accounts/index.html'
#     context = {'title':'tarsk'}
#     return render(request,template_name,context)


# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.save()
#             login(request, user, backend='django.contrib.auth.backends.ModelBackend')
#             print(f'created user: {user} \n current user: {request.user}')
#             return redirect('accounts:login')
#     else:
#         form = UserCreationForm()
#     return render(request, 'accounts/signup.html', {'signup_form': form,'title':'dashboard'})


# def login_view(request,backend = 'django.contrib.auth.backends.ModelBackend'):
#     form = LoginForm()
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
        
#         if form.is_valid():
#             user = authenticate(
#                 email=form.cleaned_data['email'],
#                 password=form.cleaned_data['password'],
#             )
#             if user is not None:
#                 login(request, user)
#                 user.profile.online = True
#                 user.profile.save()
#                 messages.info(request, "login successful!")
#                 if user.profile.first_name == None:
#                     return redirect('accounts:edit_profile')
#                 if 'user_settings' in request.POST:
#                     return redirect('accounts:settings')
                
#             else:
#                 messages.info(request, "login failed!")
                
#             return redirect('index')
        
#     return render(request, 'accounts/login.html', context={'form': LoginForm,'title':'login'})


# def edit_profile(request):
#     form = ProfileEditForm(request.POST or None, instance=request.user.profile)
#     from_signup = False
#     if request.user.profile.first_name == None:
#         from_signup = True

#     if request.POST:    
#         if form.is_valid():
#             profile = form
#             profile.save()
#             messages.info(request, "profile information updated")
#             if from_signup:
#                 # return redirect('task:dashboard')  
#                 return redirect('accounts:dashboard')
#             return redirect('accounts:settings')
            
#         else:
#             messages.info(request, "please check provided information")

#     template_name = 'accounts/edit_profile.html'
#     context = {'form':form}
#     return render(request,template_name,context)

# @login_required(login_url='index')
# def settings(request,slug=email):
#     user = request.user
#     form = ProfileEditForm(request.POST or None, instance=user.profile)
#     template_name = 'accounts/settings.html'
#     context = {'title':f'{user.profile.first_name} | profile', 'user':user, 'form':form}
#     return render(request,template_name,context)


# @login_required(login_url='index')         
# def logout_view(request):
#     request.user.profile.online=False
#     request.user.profile.save()
#     logout(request)
#     return redirect('index')


# @login_required(login_url='index')
# def delete_account(request):
#     if request.user.is_authenticated:
#         user = request.user
#         user.delete()
#         return redirect('index')