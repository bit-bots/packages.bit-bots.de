from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.template.response import TemplateResponse

from packages.models import Package


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'packages/index.html', {'packages': Package.objects.all()})
