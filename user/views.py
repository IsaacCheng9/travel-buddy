from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import UserRegisterForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Your account has successfully been created! You are now "
                "able to log in.",
            )
            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, "user/register.html", {"form": form})
