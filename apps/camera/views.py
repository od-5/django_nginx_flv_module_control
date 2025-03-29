from django.http import JsonResponse


def check_status(request):
    return JsonResponse({'status': '200 OK'})
