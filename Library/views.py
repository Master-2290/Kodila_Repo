from django.http import HttpResponse


def home(request):
    return HttpResponse("Bienvenue dans l'application Library.")
