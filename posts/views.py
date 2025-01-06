from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Post
import json

@csrf_exempt
def get_users(request):
    try:
        users = list(User.objects.values('id', 'username', 'email', 'created_at'))
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.db import transaction, IntegrityError

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            with transaction.atomic():
                # Check if email already exists
                if User.objects.filter(email=data['email']).exists():
                    return JsonResponse({
                        'error': 'Email already exists'
                    }, status=400)
                    
                # Check if username already exists
                if User.objects.filter(username=data['username']).exists():
                    return JsonResponse({
                        'error': 'Username already exists'
                    }, status=400)
                    
                user = User.objects.create(
                    username=data['username'],
                    email=data['email']
                )
                return JsonResponse({
                    'id': user.id,
                    'message': 'User created successfully'
                }, status=201)
                
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                return JsonResponse({
                    'error': 'Email or username already exists'
                }, status=400)
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def get_posts(request):
    try:
        posts = list(Post.objects.values('id', 'content', 'author', 'created_at'))
        return JsonResponse(posts, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            author = User.objects.get(id=data['author'])
            post = Post.objects.create(
                content=data['content'],
                author=author
            )
            return JsonResponse({
                'id': post.id,
                'message': 'Post created successfully'
            }, status=201)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Author not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
