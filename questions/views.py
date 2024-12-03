from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin  # Correct mixin for class-based views
from .models import Question, Tag, QuestionTag
from django.urls import reverse_lazy
from .forms import QuestionForm



class QuestionListView(ListView):
    model = Question
    template_name = 'questions/question_list.html'
    context_object_name = 'questions'

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'questions/question_detail.html'
    context_object_name = 'question'

class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'questions/question_form.html'
    success_url = reverse_lazy('question_list')

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