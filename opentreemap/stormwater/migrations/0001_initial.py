# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('treemap', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PolygonalMapFeature',
            fields=[
                ('mapfeature_ptr',
                 models.OneToOneField(
                     parent_link=True,
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     to='treemap.MapFeature',
                     on_delete=models.CASCADE)),
                ('polygon',
                 django.contrib.gis.db.models.fields.MultiPolygonField(
                     srid=3857)),
            ],
            options={
                'abstract': False,
            },
            bases=(
                'treemap.mapfeature',
            ),
        ),
        migrations.CreateModel(
            name='Bioswale',
            fields=[
                ('polygonalmapfeature_ptr',
                 models.OneToOneField(
                     parent_link=True,
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     to='stormwater.PolygonalMapFeature',
                     on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=(
                'stormwater.polygonalmapfeature',
            ),
        ),
    ]
