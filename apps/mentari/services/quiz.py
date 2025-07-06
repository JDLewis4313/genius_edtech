from django.urls import reverse
import random

def handle_quiz_request(message, user=None, session=None):
    try:
        from apps.quiz.models import Topic, Question

        if not session:
            return {"response": "<div class='alert alert-danger'>Session error. Please refresh and try again.</div>"}

        message_lower = message.lower()

        if session.get('quiz_active'):
            return handle_quiz_answer(message, user, session)

        matched_topic = match_topic_from_message(message_lower)
        if matched_topic:
            question_pool = list(Question.objects.filter(topic=matched_topic).values_list('id', flat=True))
            if question_pool:
                random.shuffle(question_pool)
                quiz_questions = question_pool[:min(5, len(question_pool))]
                first_question_id = quiz_questions[0]

                session['quiz_active'] = True
                session['quiz_topic_id'] = matched_topic.id
                session['quiz_topic_name'] = matched_topic.title
                session['quiz_questions'] = quiz_questions
                session['quiz_current_index'] = 0
                session['quiz_score'] = 0
                session['quiz_total'] = len(quiz_questions)
                session['quiz_incorrect_streak'] = 0

                first_question = Question.objects.get(id=first_question_id)

                intro = f"<div class='alert alert-primary'><strong>🎯 Starting quiz on {matched_topic.title}</strong><br>"
                intro += f"You'll have {session['quiz_total']} questions. Good luck!</div><br>"

                question_data = format_quiz_question(first_question, 1, session['quiz_total'])
                question_data['response'] = intro + question_data['text']
                del question_data['text']

                return question_data
            else:
                return {"response": f"<div class='alert alert-warning'>No questions available for {matched_topic.title}</div>"}

        topics = Topic.objects.filter(questions__isnull=False).distinct()[:10]
        response = "<div class='alert alert-info'><strong>Available quiz topics:</strong><br><ul>"
        for topic in topics:
            response += f"<li>{topic.title}</li>"
        response += "</ul><br>Try saying 'quiz on [topic name]'</div>"

        return {
            "response": response,
            "card": {
                "type": "topic_list",
                "topics": [{"id": t.id, "title": t.title} for t in topics]
            }
        }

    except Exception as e:
        return {"response": f"<div class='alert alert-danger'>Quiz error: {str(e)}</div>"}


def match_topic_from_message(message_lower):
    from apps.quiz.models import Topic

    # Only try to match if the message clearly indicates a quiz
    quiz_signals = ['quiz on', 'test on', 'start quiz on', 'give me a quiz on']
    if not any(message_lower.startswith(sig) for sig in quiz_signals):
        return None

    stop_words = ['quiz', 'on', 'test', 'me', 'about', 'the', 'a', 'an', 'give', 'start']
    words = message_lower.split()
    content_words = [w for w in words if w not in stop_words]

    for topic in Topic.objects.all():
        title_lower = topic.title.lower()
        for word in content_words:
            if word in title_lower:
                return topic
        topic_words = title_lower.split()
        for topic_word in topic_words:
            if len(topic_word) > 3 and topic_word in message_lower:
                return topic
    return None



def format_quiz_question(question, question_num, total):
    choices = question.choices.all()
    return {
        "text": f"<strong>Question {question_num} of {total}:</strong> {question.text}",
        "card": {
            "type": "quiz_question",
            "question_id": question.id,
            "question_num": question_num,
            "total": total,
            "choices": [
                {
                    "id": choice.id,
                    "text": choice.text,
                    "letter": chr(65 + i)
                }
                for i, choice in enumerate(choices)
            ]
        }
    }


def handle_quiz_answer(message, user, session):
    try:
        from apps.quiz.models import Question, Choice

        answer_text = message.lower().strip()
        if answer_text.startswith('answer:'):
            answer_text = answer_text.replace('answer:', '').strip()

        current_index = session.get('quiz_current_index', 0)
        quiz_questions = session.get('quiz_questions', [])

        if not quiz_questions or current_index >= len(quiz_questions):
            return handle_quiz_complete(session, user)

        question_id = quiz_questions[current_index]
        question = Question.objects.get(id=question_id)
        choices = list(question.choices.all())

        selected_choice = None
        if len(answer_text) == 1 and answer_text.isalpha():
            index = ord(answer_text.upper()) - 65
            if 0 <= index < len(choices):
                selected_choice = choices[index]
        else:
            for choice in choices:
                if answer_text.lower() in choice.text.lower():
                    selected_choice = choice
                    break

        if not selected_choice:
            q_data = format_quiz_question(question, current_index + 1, session['quiz_total'])
            return {
                "response": "<div class='alert alert-warning'>Please answer with A, B, C, or D (or click on an option)</div><br>" + q_data['text'],
                "card": q_data['card']
            }

        is_correct = selected_choice.is_correct
        if is_correct:
            session['quiz_score'] += 1
            session['quiz_incorrect_streak'] = 0
            feedback = "<div class='alert alert-success'><strong>✅ Correct!</strong></div>"
        else:
            session['quiz_incorrect_streak'] = session.get('quiz_incorrect_streak', 0) + 1
            correct_choice = next((c for c in choices if c.is_correct), None)
            feedback = f"<div class='alert alert-danger'><strong>❌ Incorrect.</strong> The correct answer was: <strong>{correct_choice.text}</strong></div>"

        if question.explanation:
            feedback += f"<div class='alert alert-info mt-2'><strong>📚 Explanation:</strong> {question.explanation}</div>"

        session['quiz_current_index'] = current_index + 1

        if session['quiz_current_index'] >= len(quiz_questions):
            return handle_quiz_complete(session, user, feedback)

        next_question_id = quiz_questions[session['quiz_current_index']]
        next_question = Question.objects.get(id=next_question_id)
        next_q_data = format_quiz_question(next_question, session['quiz_current_index'] + 1, session['quiz_total'])

        return {
            "response": f"{feedback}<br><br>{next_q_data['text']}",
            "card": next_q_data['card']
        }

    except Exception as e:
        return {"response": f"<div class='alert alert-danger'>Error processing answer: {str(e)}</div>"}



def get_smart_recommendations(percentage, topic_name, user):
    """Generate smart recommendations based on quiz performance"""
    recommendations = []
    
    if percentage >= 90:
        recommendations.extend([
            f"🌟 Excellent work on {topic_name}! Try a more advanced topic.",
            "🚀 You're ready for challenge problems!",
            "📚 Consider exploring related concepts."
        ])
    elif percentage >= 70:
        recommendations.extend([
            f"👍 Good job on {topic_name}! A few more practice questions could help.",
            "🎯 Try reviewing the concepts you missed.",
            "📖 Some additional study could boost your score."
        ])
    elif percentage >= 50:
        recommendations.extend([
            f"📚 {topic_name} needs more practice. Don't give up!",
            "🔍 Review the explanations for missed questions.",
            "💡 Try starting with easier questions in this topic."
        ])
    else:
        recommendations.extend([
            f"🌱 {topic_name} is challenging - that's okay! Learning takes time.",
            "📖 Consider reviewing the basics first.",
            "💪 Practice makes perfect - try again when you're ready."
        ])
    
    return recommendations[:2]  # Return top 2 recommendations


def handle_quiz_complete(session, user, feedback=None):
    score = session.get('quiz_score', 0)
    total = session.get('quiz_total', 0)
    topic_name = session.get('quiz_topic_name', 'Unknown Topic')
    percentage = (score / total * 100) if total > 0 else 0
    incorrect_streak = session.get('quiz_incorrect_streak', 0)

    if user and user.is_authenticated and 'quiz_topic_id' in session:
        from apps.quiz.models import QuizAttempt
        QuizAttempt.objects.create(
            user=user,
            topic_id=session['quiz_topic_id'],
            score=percentage
        )

    encouragement = ""
    if incorrect_streak >= 2:
        encouragement = """
        <div class='alert alert-warning mt-3'>
            <strong>💡 Keep going!</strong><br>
            Mistakes are part of learning. Want to review the questions you missed or try a related topic?
        </div>
        """

    for key in ['quiz_active', 'quiz_topic_id', 'quiz_topic_name', 'quiz_questions',
                'quiz_current_index', 'quiz_score', 'quiz_total', 'quiz_incorrect_streak']:
        session.pop(key, None)

    recommendations = get_smart_recommendations(percentage, topic_name, user)
    
    if percentage >= 80:
        emoji = "🏆"
        message = "Excellent work! You've mastered this topic!"
    elif percentage >= 60:
        emoji = "😊"
        message = "Good job! You're getting there!"
    else:
        emoji = "📚"
        message = "Keep practicing! You'll improve with time!"

    final_message = (feedback + "<br><br>" if feedback else "") + \
        f"<div class='alert alert-primary text-center'>" + \
        f"<h4>{emoji} Quiz Complete!</h4>" + \
        f"<p class='mb-2'>Topic: <strong>{topic_name}</strong></p>" + \
        f"<p class='mb-0'>Your score: <strong>{score}/{total}</strong> ({percentage:.0f}%)</p>" + \
        f"<p class='mt-2'>{message}</p></div>" + encouragement

    return {
        "response": final_message,
        "card": {
            "type": "quiz_complete",
            "score": score,
            "total": total,
            "percentage": percentage,
            "topic": topic_name,
            "recommendations": recommendations,
            "next_actions": [
                {"text": "🔄 Try Another Quiz", "action": "start a new quiz"},
                {"text": "📊 View Progress", "action": "How am I doing?"},
                {"text": "🎯 Practice More", "action": f"more practice on {topic_name}"}
            ]
        }
    }
