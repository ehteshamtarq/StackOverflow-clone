from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm
from django.db.models import Count
import markdown2
from questions.models import Question, Answer, Comment
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Profile
from .services import calculate_reputation
from django.db.models import Q


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

    if request.user.is_authenticated:
        reputation = calculate_reputation(request.user)
        user_profile = request.user.profile

    else:
        reputation = 0
        user_profile = None

    for question in latest_questions:
        question.body_clean = markdown2.markdown(question.body)

    return render(request, 'user/main.html', {'latest_questions': latest_questions, 'reputation': reputation, 'user_profile': user_profile})

def profile(request, username=None):
    if username is None:

        if not request.user.is_authenticated:
            raise Http404("User not found.")
        user_profile = request.user.profile
        profile_user = request.user
    else:

        profile_user = get_object_or_404(User, username=username)
        user_profile = profile_user.profile

    reputation = calculate_reputation(profile_user)
    comment_count = Comment.objects.filter(user=profile_user).count()
    question_count = Question.objects.filter(user=profile_user).count()
    answer_count = Answer.objects.filter(user=profile_user).count()
    answered_questions = Question.objects.filter(answers__user=profile_user).distinct()
    user_questions = Question.objects.filter(user=profile_user)

    context = {
        'profile': user_profile,
        'profile_user': profile_user,
        'comment_count': comment_count,
        'question_count': question_count,
        'answer_count': answer_count,
        'answered_questions': answered_questions,
        'user_questions': user_questions,
        'reputation': reputation,
        'user_profile': user_profile
    }

    return render(request, 'user/profile.html', context)

def search_view(request):
    query = request.GET.get('query', '')
    questions = Question.objects.all()

    if query:
        if query.startswith('[') and query.endswith(']'):
            tag_name = query.strip('[]')
            questions = Question.objects.filter(tags__tag__name__icontains=tag_name)
        elif query.startswith('"') and query.endswith('"'):
            phrase = query.strip('"')
            questions = questions.filter(Q(title__icontains=phrase) | Q(body__icontains=phrase))
        else:
            questions = questions.filter(
                Q(title__icontains=query) | Q(body__icontains=query)).distinct()

    user_profile = request.user.profile

    for question in questions:
        question.body_clean = markdown2.markdown(question.body)

    return render(request, 'user/search_results.html', {'questions': questions, 'query': query, 'user_profile': user_profile})

@login_required
def edit_profile(request, username):
    profile = get_object_or_404(Profile, user__username=username)

    if request.user != profile.user:
        return HttpResponseForbidden("You are not allowed to edit this profile.")

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('user:profile', username=username)

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    user_profile = request.user.profile
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user_profile': user_profile
    }

    return render(request, 'user/edit-profile.html', context)
