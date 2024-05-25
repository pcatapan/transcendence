import os
import json
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.views.decorators.http import require_GET, require_POST
#from django.views.decorators.csrf import requires_csrf_token
from django.shortcuts import get_object_or_404

from api.authuser.models.custom_user import CustomUser
from api.authuser.models.friendship import Friendship

from .validation.user_validator import UserUpdateValidator
from .utils.image import is_valid_image, save_avatar_from_url

@require_GET
def show(request, user_id) :
	user = get_object_or_404(CustomUser, pk=user_id)

	return JsonResponse({'data':user.to_json_full()}, status=200)

@require_POST
def update_avatar(request):
    user = request.user
    
    if 'avatar' in request.FILES:
        avatar = request.FILES['avatar']
        valid, error_message = is_valid_image(avatar)
        if not valid:
            return JsonResponse({
                'message': error_message
            }, status=400)

        #unique_filename = get_unique_filename(avatar.name)
        user.update_avatar(avatar)
        return JsonResponse({
            'message': 'Avatar updated successfully',
            'data': user.to_json()
        }, status=200)

    elif 'avatar_url' in request.POST:
        avatar_url = request.POST['avatar_url']
        filename, error_message = save_avatar_from_url(avatar_url)
        if not filename:
            return JsonResponse({
                'message': error_message
            }, status=400)
        
        user.avatar.save(filename, ContentFile(filename))
        return JsonResponse({
            'message': 'Avatar updated successfully'
        }, status=200)

    return JsonResponse({
        'message': 'Missing avatar or avatar_url in request'
    }, status=400)

@require_POST
def update(request):

    if not request.body:
        return JsonResponse({
            'message': 'Empty payload'
        }, status=400)

    user = request.user

    try:
        data = json.loads(request.body)
        data['id'] = user.id

    except json.JSONDecodeError:
        return JsonResponse({
            'message': "Invalid JSON"
        }, status=400)

    input_errors = UserUpdateValidator(data).validate()
    if input_errors:
        return JsonResponse({
            "message": "Something went wrong",
            "data": input_errors
        }, status=403)

    user.username = data.get("username")
    user.email = data.get("email")
    user.fullname = data.get("fullname")

    user.save()

    return JsonResponse({
        "message": "User updated successfully",
        "data": user.to_json()
    }, status=200)

@require_GET
def user_friends_list(request):

    user = request.user

    try:
        friendship = Friendship.objects.get(user=user)
        friends = friendship.friends.all()
        
        friend_list = []

        user_id_before_loop = user.id

        for friendship in friends:
            if friendship.id != user_id_before_loop:
                friend_list.append({
                    'id': friendship.id,
                    'username': friendship.username,
                    'fullnmae': friendship.fullname
                })

        return JsonResponse({
            'data': friend_list
        }, status=200)

    except Friendship.DoesNotExist:
        return JsonResponse({
            'message': 'User has no friends',
            'data': []
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'message': str(e)
        }, status=500)
    
@require_POST
def user_friends_add(request):

    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({
            'message': 'Missing user_id in request'
        }, status=400)
    
    user = request.user
    friend = get_object_or_404(CustomUser, pk=user_id)

    try:
        friendship, created = Friendship.objects.get_or_create(user=user)
        if user in friendship.blocked_users.all() or friend in friendship.blocked_users.all():
            return JsonResponse({
                'message': 'User is blocked'
            }, status=403)
    except Exception as e:
        return JsonResponse({
            'message': str(e)
        }, status=500)

    try:
        friendship = Friendship.objects.get(user=user)
        friendship.friends.add(friend)
        return JsonResponse({
            'message': 'Friend added successfully',
            'data': friendship.to_json()
        }, status=200)
    except Friendship.DoesNotExist:
        return JsonResponse({
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': str(e)
        }, status=500)
    
@require_POST
def user_friends_remove(request):

    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({
            'message': 'Missing user_id in request'
        }, status=400)

    user = request.user
    friend = get_object_or_404(CustomUser, pk=user_id)

    try:
        friendship = Friendship.objects.get(user=user)
        if friend in friendship.friends.all():
            friendship.friends.remove(friend)
            friendship.save()
            return JsonResponse({
                'message': 'Friend removed successfully',
                'data': friendship.to_json()
            }, status=200)
        else:
            return JsonResponse({
                'message': 'User is not a friend'
            }, status=403)
    except Friendship.DoesNotExist:
        return JsonResponse({
            'message': 'User has no friends'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': str(e)
        }, status=500)
    
@require_GET
def user_blocked_list(request):
    
        user = request.user
    
        try:
            friendship = Friendship.objects.get(user=user)
            blocked_users = friendship.blocked_users.all()
            
            blocked_users_list = []
    
            for blocked_user in blocked_users:
                blocked_users_list.append({
                    'id': blocked_user.id,
                    'username': blocked_user.username,
                    'fullnmae': blocked_user.fullname
                })
    
            return JsonResponse({
                'data': blocked_users_list
            }, status=200)
    
        except Friendship.DoesNotExist:
            return JsonResponse({
                'message': 'User has no blocked users',
                'data': []
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'message': str(e)
            }, status=500)

@require_POST
def user_blocked_add(request):

    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({
            'message': 'Missing user_id in request'
        }, status=400)

    user = request.user
    blocked_user = get_object_or_404(CustomUser, pk=user_id)

    try:
        friendship = Friendship.objects.get(user=user)
        friendship.blocked_users.add(blocked_user)
        return JsonResponse({
            'message': 'User blocked successfully',
            'data': friendship.to_json()
        }, status=200)
    except Friendship.DoesNotExist:
        return JsonResponse({
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': str(e)
        }, status=500)
    
@require_POST
def user_blocked_remove(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({
            'message': 'Missing user_id in request'
        }, status=400)

    user = request.user
    blocked_user = get_object_or_404(CustomUser, pk=user_id)

    try:
        friendship = Friendship.objects.get(user=user)
        friendship.blocked_users.remove(blocked_user)
        return JsonResponse({
            'message': 'User unblocked successfully',
            'data': friendship.to_json()
        }, status=200)
    except Friendship.DoesNotExist:
        return JsonResponse({
            'message': 'User has no blocked users'
        }, status=403)
    except Exception as e:
        return JsonResponse({
            'message': str(e)
        }, status=500)