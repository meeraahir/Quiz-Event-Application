from django.contrib.auth.models import User
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Quiz, UserSubmission, Event, UserAnswer, Answer, Question
from .serializers import (
    RegisterSerializer, QuizSerializer, EventSerializer, UserSubmissionSerializer,
    UserAnswerSerializer, QuizSubmissionSerializer, QuizCreateSerializer,
    QuestionCreateSerializer, AnswerCreateSerializer, EventCreateSerializer,
    QuestionSerializer, AnswerSerializer
)


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class UserSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserSubmission.objects.all()
    serializer_class = UserSubmissionSerializer


class UserAnswerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserAnswer.objects.all()
    serializer_class = UserAnswerSerializer


class QuizSubmissionApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.data:
            return Response(
                {'detail': 'Request data is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = QuizSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        quiz_id = serializer.validated_data.get('quiz_id')
        answers = serializer.validated_data.get('answers', {})
        user = request.user

        if not quiz_id:
            return Response(
                {'detail': 'Quiz ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not answers:
            return Response(
                {'detail': 'Answers are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({'detail': 'Quiz does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return Response(
                {'detail': 'Invalid quiz ID format.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if UserSubmission.objects.filter(quiz=quiz, user_name=user).exists():
            return Response(
                {'detail': 'You have already completed this quiz.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not quiz.questions.exists():
            return Response(
                {'detail': 'This quiz has no questions available.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        submission = UserSubmission.objects.create(
            quiz=quiz,
            user_name=user,
            score=0
        )
        score = 0

        for question in quiz.questions.all():
            question_key = str(question.id)
            
            if question_key not in answers:
                submission.delete()
                return Response(
                    {'detail': f'Missing answer for question: {question.text[:50]}...'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            answer_value = answers[question_key]
            
            if answer_value is None:
                submission.delete()
                return Response(
                    {'detail': f'Answer cannot be null for question: {question.text[:50]}...'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not isinstance(answer_value, str):
                answer_value = str(answer_value)
            
            answer_value = answer_value.strip()

            if question.question_type == "MCQ":
                if not answer_value or answer_value == '':
                    submission.delete()
                    return Response(
                        {'detail': f'Please answer question: {question.text[:50]}...'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                try:
                    answer_id = int(answer_value)
                except (ValueError, TypeError):
                    submission.delete()
                    return Response(
                        {'detail': f'Invalid answer format for question: {question.text[:50]}. Expected a numeric answer ID.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if answer_id <= 0:
                    submission.delete()
                    return Response(
                        {'detail': f'Answer ID must be a positive integer for question: {question.text[:50]}...'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                try:
                    selected_answer = Answer.objects.get(id=answer_id)
                except Answer.DoesNotExist:
                    submission.delete()
                    return Response(
                        {'detail': f'Selected answer does not exist for question: {question.text[:50]}...'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if selected_answer.question != question:
                    submission.delete()
                    return Response(
                        {'detail': f'Invalid answer selected. Answer does not belong to question: {question.text[:50]}...'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                correct = selected_answer.is_correct
                if correct:
                    score += 1

                UserAnswer.objects.create(
                    submission=submission,
                    question=question,
                    answer=selected_answer,
                    is_correct=correct,
                )
            elif question.question_type == "TEXT":
                if not answer_value or answer_value == '':
                    submission.delete()
                    return Response(
                        {'detail': f'Please provide an answer for: {question.text[:50]}...'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if len(answer_value) > 1000:
                    submission.delete()
                    return Response(
                        {'detail': f'Text answer is too long. Maximum 1000 characters allowed for question: {question.text[:50]}...'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                UserAnswer.objects.create(
                    submission=submission,
                    question=question,
                    answer=None,
                    is_correct=False,
                )
            else:
                submission.delete()
                return Response(
                    {'detail': f'Unknown question type for question: {question.text[:50]}...'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        submission.score = score
        submission.save()

        submission_serializer = UserSubmissionSerializer(submission)
        return Response({
            'message': 'Quiz submitted successfully',
            'submission': submission_serializer.data
        }, status=status.HTTP_201_CREATED)


class QuizCreateApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.data:
            return Response(
                {'detail': 'Request data is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = QuizCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        quiz = serializer.save()
        quiz_serializer = QuizSerializer(quiz)
        
        return Response({
            'message': 'Quiz created successfully',
            'quiz': quiz_serializer.data
        }, status=status.HTTP_201_CREATED)


class QuestionCreateApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.data:
            return Response(
                {'detail': 'Request data is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = QuestionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.save()
        question_serializer = QuestionSerializer(question)
        
        return Response({
            'message': 'Question created successfully',
            'question': question_serializer.data
        }, status=status.HTTP_201_CREATED)


class AnswerCreateApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.data:
            return Response(
                {'detail': 'Request data is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AnswerCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        answer = serializer.save()
        answer_serializer = AnswerSerializer(answer)
        
        return Response({
            'message': 'Answer created successfully',
            'answer': answer_serializer.data
        }, status=status.HTTP_201_CREATED)


class EventCreateApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.data:
            return Response(
                {'detail': 'Request data is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = EventCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        event = serializer.save()
        event_serializer = EventSerializer(event)
        
        return Response({
            'message': 'Event created successfully',
            'event': event_serializer.data
        }, status=status.HTTP_201_CREATED)
