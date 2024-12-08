from questions.models import Question, Answer, Vote

def calculate_reputation(user):
    reputation = 0

    reputation += Question.objects.filter(user=user).count() * 20

    reputation += Answer.objects.filter(user=user).count() * 10

    upvotes_on_questions = Vote.objects.filter(user=user, vote_type='upvote').count()
    downvotes_on_questions = Vote.objects.filter(user=user, vote_type='downvote').count()
    reputation += upvotes_on_questions * 5
    reputation -= downvotes_on_questions * 2

    # Calculate points for upvotes and downvotes on answers
    # upvotes_on_answers = Vote.objects.filter(user=user, vote_type='upvote', answer__user=user).count()
    # downvotes_on_answers = Vote.objects.filter(user=user, vote_type='downvote', answer__user=user).count()
    # reputation += upvotes_on_answers * 5
    # reputation -= downvotes_on_answers * 2

    return reputation