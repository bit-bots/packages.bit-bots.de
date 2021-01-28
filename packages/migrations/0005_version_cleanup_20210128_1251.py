import re
from django.db import migrations, models
from packages.models import Package


def forwards(apps, schema_editor):
    if schema_editor.connection.alias != 'default':
        return
    for package in Package.objects.all():
        package.version = re.match(r'^\d+\.\d+(\.\d+)?(-\d+)?', package.version).group(0)
        package.save()


class Migration(migrations.Migration):
    dependencies = [
        ('packages', '0004_auto_20200128_1519'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
