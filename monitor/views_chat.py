from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import ChatMessage, CustomUser
import json


@login_required(login_url='login')
def chat_list(request):
    """
    Vista para listar conversaciones.
    - Si es admin/root: muestra lista de todos los usuarios
    - Si es usuario regular: muestra solo el root
    """
    user = request.user
    
    if user.is_staff or user.is_superuser:
        # Admin ve lista de todos los usuarios
        users_list = CustomUser.objects.exclude(id=user.id).order_by('email')
        template = 'chat/admin_chat_list.html'
    else:
        # Usuario regular solo ve el admin/root
        root_users = CustomUser.objects.filter(is_superuser=True)
        users_list = root_users
        template = 'chat/user_chat_list.html'
    
    # Contar mensajes no leídos
    unread_count = ChatMessage.objects.filter(
        recipient=user,
        is_read=False
    ).count()
    
    # Obtener última conversación de cada usuario
    conversations = []
    for other_user in users_list:
        last_message = ChatMessage.objects.filter(
            Q(sender=user, recipient=other_user) |
            Q(sender=other_user, recipient=user)
        ).order_by('-created_at').first()
        
        unread = ChatMessage.objects.filter(
            sender=other_user,
            recipient=user,
            is_read=False
        ).count()
        
        conversations.append({
            'user': other_user,
            'last_message': last_message,
            'unread': unread
        })
    
    # Ordenar por último mensaje
    conversations.sort(
        key=lambda x: x['last_message'].created_at if x['last_message'] else timezone.now(),
        reverse=True
    )
    
    return render(request, template, {
        'conversations': conversations,
        'unread_count': unread_count,
    })


@login_required(login_url='login')
def chat_detail(request, user_id):
    """
    Vista para ver la conversación entre dos usuarios.
    """
    user = request.user
    other_user = get_object_or_404(CustomUser, id=user_id)
    
    # Validación de permisos
    if not user.is_staff and not user.is_superuser:
        if not other_user.is_superuser:
            return redirect('chat_list')
    
    # Obtener mensajes
    messages = ChatMessage.objects.filter(
        Q(sender=user, recipient=other_user) |
        Q(sender=other_user, recipient=user)
    ).order_by('created_at')
    
    # Marcar mensajes como leídos
    ChatMessage.objects.filter(
        sender=other_user,
        recipient=user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return render(request, 'chat/chat_detail.html', {
        'other_user': other_user,
        'messages': messages,
    })


@login_required(login_url='login')
@require_POST
def send_message(request, user_id):
    """
    API para enviar un mensaje.
    """
    user = request.user
    recipient = get_object_or_404(CustomUser, id=user_id)
    
    # Validación de permisos
    if not user.is_staff and not user.is_superuser:
        if not recipient.is_superuser:
            return JsonResponse({'error': 'No permitido'}, status=403)
    
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return JsonResponse({'error': 'El mensaje está vacío'}, status=400)
        
        if len(message_text) > 5000:
            return JsonResponse({'error': 'El mensaje es muy largo'}, status=400)
        
        message = ChatMessage.objects.create(
            sender=user,
            recipient=recipient,
            message=message_text
        )
        
        return JsonResponse({
            'id': message.id,
            'message': message.message,
            'created_at': message.created_at.isoformat(),
            'sender_id': message.sender.id,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required(login_url='login')
def get_unread_count(request):
    """
    API para obtener el count de mensajes no leídos.
    """
    unread_count = ChatMessage.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'unread_count': unread_count})


@login_required(login_url='login')
def get_new_messages(request, user_id):
    """
    API para obtener nuevos mensajes (para polling/actualización).
    """
    user = request.user
    other_user = get_object_or_404(CustomUser, id=user_id)
    last_message_id = request.GET.get('last_message_id', 0)
    
    messages = ChatMessage.objects.filter(
        Q(sender=user, recipient=other_user) |
        Q(sender=other_user, recipient=user),
        id__gt=last_message_id
    ).order_by('created_at').values(
        'id', 'sender_id', 'recipient_id', 'message', 'created_at', 'is_read'
    )
    
    # Marcar como leídos
    ChatMessage.objects.filter(
        sender=other_user,
        recipient=user,
        is_read=False,
        id__gt=last_message_id
    ).update(is_read=True, read_at=timezone.now())
    
    return JsonResponse({
        'messages': list(messages)
    }, safe=False)
