from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from .models import Patrol
from django.shortcuts import get_object_or_404


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account created for {username}!")
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        pic = request.FILES.get("myfile")

        profil = get_object_or_404(Patrol, user=request.user)
        profil.image = pic
        profil.save(update_fields=["image"])
        return render(request, "users/profile.html")
    else:
        return render(request, "users/profile.html")


from django.shortcuts import render

# Create your views here.
