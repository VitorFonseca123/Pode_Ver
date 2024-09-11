from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def AddMovie(request):
    return HttpResponse("Ola mundo!")