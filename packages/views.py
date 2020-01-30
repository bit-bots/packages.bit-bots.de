from django import urls
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse

from packages.models import Package, LocalState


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'packages/index.html', {'packages': Package.objects.order_by('upstream_state', 'name')})


def package(request: HttpRequest, package_name: str) -> HttpResponse:
    package = get_object_or_404(Package, name=package_name)
    return render(request, 'packages/package.html', {'package': package})


def request(request: HttpRequest, package_name: str) -> HttpResponse:
    package = get_object_or_404(Package, name=package_name)
    package.local_state = LocalState.QUEUED
    package.save()
    return redirect(urls.reverse('package', args=(package_name,)))
