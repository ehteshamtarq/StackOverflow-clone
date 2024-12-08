import markdown2
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Question, Tag, QuestionTag, Answer, Comment, Vote
from django.urls import reverse_lazy
from .forms import AnswerForm, CommentForm, QuestionForm, QuestionEditDeleteForm
from django.shortcuts import redirect, get_object_or_404,render
from django.http import JsonResponse,HttpResponseForbidden
from django.views import View
from django.db.models import Count
from user.models import Profile
from user.services import calculate_reputation

class QuestionListView(ListView):
    model = Question
    template_name = 'question_list.html'
    context_object_name = 'questions'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = (
            Question.objects
            .select_related('user')
            .annotate(answer_count=Count('answers'))
            .prefetch_related('tags')
            .order_by('-created_at')
        )
        for question in queryset:
            question.body_clean = markdown2.markdown(question.body)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_questions'] = Question.objects.count()
        context['user_profile'] = get_object_or_404(Profile, user=self.request.user)
        return context

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'questions/question_detail.html'
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answer_form'] = AnswerForm()
        context['comment_form'] = CommentForm()
        context['answers'] = self.object.answers.all()
        context['comments'] = self.object.question_comments.all()
        context['tags'] = self.object.tags.all()
        context['username'] = self.object.user.username
        context['answer_count'] = self.object.answers.count()
        context['vote_count'] = self.object.upvotes - self.object.downvotes
        context['user_profile'] = get_object_or_404(Profile, user=self.request.user)
        context['question_owner'] = self.object.user
        context['question_owner_profile'] = get_object_or_404(Profile, user=self.object.user)
        context['reputation'] = calculate_reputation(context['question_owner'])

        if self.request.user.is_authenticated:
            vote = Vote.objects.filter(user=self.request.user, question=self.object).first()
            context['user_vote'] = vote.vote_type if vote else None
        else:
            context['user_vote'] = None

        if self.request.method == 'GET':
            self.object.views += 1
            self.object.save(update_fields=['views'])

        for answer in context['answers']:
            answer.comments = Comment.objects.filter(answer=answer)
            answer.profile = get_object_or_404(Profile, user=answer.user)
            answer.reputation = calculate_reputation(answer.user)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.views > 0:
            self.object.views -= 1
            self.object.save(update_fields=['views'])

        if 'answer_submit' in request.POST:
            return self.handle_answer_submission(request)
        elif 'comment_submit' in request.POST:
            return self.handle_comment_submission(request)
        return redirect('questions:question_detail', pk=self.object.pk)

    def handle_answer_submission(self, request):
        form = AnswerForm(request.POST)
        if form.is_valid():
            if not Answer.objects.filter(user=request.user, question=self.object).exists():
                answer = form.save(commit=False)
                answer.user = request.user
                answer.question = self.object
                answer.save()
        return redirect('questions:question_detail', pk=self.object.pk)

    def handle_comment_submission(self, request):
        form = CommentForm(request.POST)
        if form.is_valid():
            target_id = request.POST.get('target_id')
            target_type = request.POST.get('target_type')
            if target_type == 'question':
                if not Comment.objects.filter(user=request.user, question=self.object).exists():
                    comment = form.save(commit=False)
                    comment.user = request.user
                    comment.question = self.object
                    comment.save()
            elif target_type == 'answer':
                answer = Answer.objects.get(pk=target_id)
                if not Comment.objects.filter(user=request.user, answer=answer).exists():
                    comment = form.save(commit=False)
                    comment.user = request.user
                    comment.answer = answer
                    comment.save()
        return redirect('questions:question_detail', pk=self.object.pk)

class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'questions/question_form.html'
    success_url = reverse_lazy('questions:question_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the user's profile (adjust based on your setup)
        context['user_profile'] = get_object_or_404(Profile, user=self.request.user)
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        question = form.save(commit=False)
        question.user = self.request.user
        question.save()

        tags = form.cleaned_data['tags']
        for tag in tags:
            QuestionTag.objects.create(question=question, tag=tag)

        # Optionally, associate the user_profile with the question if needed
        user_profile = get_object_or_404(Profile, user=self.request.user)
        question.user_profile = user_profile
        question.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)  # Debugging invalid form errors
        return super().form_invalid(form)

class TagListView(ListView):
    model = Tag
    template_name = 'tags/tag_list.html'
    context_object_name = 'tags'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = get_object_or_404(Profile, user=self.request.user)
        return context

class VoteQuestionView(View):
    def post(self, request, question_id, vote_type):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=403)

        question = get_object_or_404(Question, id=question_id)
        vote, created = Vote.objects.get_or_create(user=request.user, question=question)

        if not created:
            if vote.vote_type == vote_type:
                vote.delete()
                if vote_type == 'upvote':
                    question.upvotes -= 1
                else:
                    question.downvotes -= 1
                user_vote_type = None
            else:

                if vote.vote_type == 'upvote':
                    question.upvotes -= 1
                    question.downvotes += 1
                else:
                    question.downvotes -= 1
                    question.upvotes += 1
                vote.vote_type = vote_type
                vote.save()
                user_vote_type = vote.vote_type
        else:
            vote.vote_type = vote_type
            vote.save()
            if vote_type == 'upvote':
                question.upvotes += 1
            else:
                question.downvotes += 1
            user_vote_type = vote.vote_type

        question.save()

        return JsonResponse({
            "upvotes": question.upvotes,
            "downvotes": question.downvotes,
            "user_vote": user_vote_type
        })

class EditQuestionView(UpdateView):
    model = Question
    form_class = QuestionEditDeleteForm
    template_name = 'questions/edit_question.html'

    def get_queryset(self):
        # Ensure that only the owner can edit
        return Question.objects.filter(user=self.request.user)

    def form_valid(self, form):
        # Save the form and redirect to the question detail page
        self.object = form.save()
        return redirect('questions:question_detail', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = get_object_or_404(Profile, user=self.request.user)
        return context

class DeleteQuestionView(View):
    template_name = 'questions/confirm_delete.html'

    def get(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        if question.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this question.")

        user_profile = get_object_or_404(Profile, user=request.user)
        return render(request, self.template_name, {'question': question, 'user_profile': user_profile})

    def post(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        if question.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this question.")
        question.delete()
        return redirect('questions:question_list')

class EditAnswerView(UpdateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'questions/edit_answer.html'

    def get_queryset(self):
        return Answer.objects.filter(user=self.request.user)

    def form_valid(self, form):
        self.object = form.save()

        return redirect('questions:question_detail', pk=self.object.question.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = self.object.question
        context['user_profile'] = get_object_or_404(Profile, user=self.request.user)
        return context

class DeleteAnswerView(View):
    template_name = 'questions/confirm_delete_answer.html'

    def get(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        if answer.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this question.")

        user_profile = get_object_or_404(Profile, user=request.user)
        return render(request, self.template_name, {'answer': answer, 'user_profile': user_profile})

    def post(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        if answer.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this question.")
        answer.delete()
        return redirect('questions:question_list')

class DeleteCommentView(View):
    template_name = 'questions/confirm_delete_comment.html'

    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)

        if comment.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this comment.")

        user_profile = get_object_or_404(Profile, user=request.user)
        return render(request, self.template_name, {'comment': comment, 'user_profile': user_profile})

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)

        if comment.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this comment.")

        if comment.answer:
            answer = comment.answer
            comment.delete()
            return redirect('questions:question_detail', pk=answer.question.pk)
        elif comment.question:
            question = comment.question
            comment.delete()
            return redirect('questions:question_detail', pk=question.pk)
        return HttpResponseForbidden("Invalid comment association.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = get_object_or_404(Profile, user=self.request.user)
        return context