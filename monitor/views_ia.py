from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from services.ai_service import ask_gemini

@csrf_exempt
def ia_chat_screen(request):
    if request.method == "POST":
        # Soportar JSON y form-data
        if request.content_type == "application/json":
            import json
            body = json.loads(request.body.decode())
            user_message = body.get("question", "")
        else:
            user_message = request.POST.get("message", "")
        ia_response = ask_gemini(user_message)
        return JsonResponse({"ok": True, "answer": ia_response})
    return render(request, "ia_chat.html")
