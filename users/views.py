from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from .models import Patrol
from WrzeszczDev.models import Plot
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect

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

    if request.user.is_authenticated:
        try:
            patrol = Patrol.objects.get(user=request.user)
        except Patrol.DoesNotExist:
            patrol = None
    else:
        patrol = None

    try:
        plot_list = Plot.objects.all().filter(owner=patrol)
    except:
        plot_list = None

    if request.method == "POST":
        pic = request.FILES.get("myfile")

        patrol = get_object_or_404(Patrol, user=request.user)
        patrol.image = pic
        patrol.save(update_fields=["image"])
        return render(request, "users/profile.html")
    else:
        return render(request, "users/profile.html" , {'patrol' : patrol, 'plot_list': plot_list})


def visit(request, patrol_name):

    if request.user.is_authenticated:
        try:
            patrol = Patrol.objects.get(user=request.user)
        except Patrol.DoesNotExist:
            patrol = None
    else:
        patrol = None

    try:
        hosting_patrol = Patrol.objects.get(name=patrol_name)
    except Patrol.DoesNotExist:
        raise Http404("Patrol Does Not Exist")

    try:
        plot_list = Plot.objects.all().filter(owner=hosting_patrol)
    except:
        plot_list = None

    if request.method == "POST":
        pic = request.FILES.get("myfile")

        patrol = get_object_or_404(Patrol, user=request.user)
        patrol.image = pic
        patrol.save(update_fields=["image"])
        return render(request, "users/profile.html")
    else:
        return render(request, "users/visit.html",
                      {'visit': patrol, 'plot_list': plot_list, 'hosting_patrol': hosting_patrol})

# Create your views here.
