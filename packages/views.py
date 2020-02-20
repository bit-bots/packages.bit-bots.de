from django import urls
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q

from packages.models import Package, LocalState, UpstreamState


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'packages/index.html', {
        'available': Package.objects.filter(upstream_state=UpstreamState.UP_TO_DATE),
        'progress': Package.objects.filter(local_state=LocalState.IN_PROGRESS),
        'queue': Package.objects.filter(local_state=LocalState.QUEUED),
        'unavailable': Package.objects.filter(Q(upstream_state=UpstreamState.ONLY_UPSTREAM) & ~Q(local_state=LocalState.IN_PROGRESS) & ~Q(local_state=LocalState.QUEUED)),
        'LOCAL_URL': settings.LOCAL_URL,
        'URL_IMPRINT': settings.URL_IMPRINT,
        'URL_PRIVACY_POLICY': settings.URL_PRIVACY_POLICY,
    })


def request(request: HttpRequest, package_name: str) -> HttpResponse:
    package = get_object_or_404(Package, name=package_name)
    package.local_state = LocalState.QUEUED
    package.save()
    return redirect(urls.reverse('index'))
