import re
from django.db import models


class UpstreamState(models.IntegerChoices):
    UPDATE_AVAILABLE = 0
    UP_TO_DATE = 1
    ONLY_UPSTREAM = 2
    UNKNOWN = 3


class LocalState(models.IntegerChoices):
    IN_PROGRESS = 0
    QUEUED = 1
    UP_TO_DATE = 2


class Package(models.Model):
    name = models.CharField(max_length=120, unique=True)
    version = models.CharField(max_length=100)
    upstream_state = models.IntegerField(choices=UpstreamState.choices, default=UpstreamState.UNKNOWN)
    local_state = models.IntegerField(choices=LocalState.choices, default=LocalState.UP_TO_DATE)

    @property
    def wiki_url(self):
        if self.name.startswith('ros-melodic-'):
            return 'https://wiki.ros.org/' + self.name.replace('ros-melodic-', '').replace('-', '_')
        else:
            return None

    @property
    def version_parsed(self):
        """An array of ints representing the version"""
        return [int(item) for item in re.split('[\.-]', self.version)]


class Dependency(models.Model):
    class Meta:
        unique_together = ['parent', 'child']

    # child depends on parent
    parent = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='rdepends')
    child = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='depends')

    build_dependency = models.BooleanField()
    run_dependency = models.BooleanField()
