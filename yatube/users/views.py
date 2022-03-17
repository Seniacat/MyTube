from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import CreationForm, ProfileEditForm
from .models import Profile


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


@login_required
def update_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=profile)
    if form.is_valid():
        form.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'users/update_profile.html', {'form': form})
