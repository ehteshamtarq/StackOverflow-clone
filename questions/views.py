from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Question, Tag, QuestionTag, Answer, Comment
from django.urls import reverse_lazy, reverse
from .forms import QuestionForm, AnswerForm, CommentForm
from django.views.generic.edit import FormMixin
from django.shortcuts import redirect

class QuestionListView(ListView):
    model = Question
    template_name = 'questions/question_list.html'
    context_object_name = 'questions'


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

        self.object.views += 1
        self.object.save(update_fields=['views'])

        for answer in context['answers']:
            answer.comments = Comment.objects.filter(answer=answer)

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

    def form_valid(self, form):
        # Save the question
        question = form.save(commit=False)
        question.user = self.request.user
        question.save()

        # Save the tags
        tags = form.cleaned_data['tags']
        for tag in tags:
            QuestionTag.objects.create(question=question, tag=tag)

        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)  # Debugging invalid form errors
        return super().form_invalid(form)


class TagListView(ListView):
    model = Tag
    template_name = 'tags/tag_list.html'
    context_object_name = 'tags'