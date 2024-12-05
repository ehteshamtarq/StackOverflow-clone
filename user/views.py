from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from questions.models import Question
from django.db.models import Count
import markdown2



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('user:login')
    else:

        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form})

def main(request):
    latest_questions = (
        Question.objects
        .select_related('user')
        .annotate(answer_count=Count('answers'))
        .prefetch_related('tags')
        .order_by('-created_at')[:10]  #
    )

    for question in latest_questions:
        question.body_clean = markdown2.markdown(question.body)

    return render(request, 'user/main.html', {'latest_questions': latest_questions})

@login_required
def profile(request):
    return render(request, 'user/profile.html')
