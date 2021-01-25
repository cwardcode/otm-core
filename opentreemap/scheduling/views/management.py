# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.shortcuts import redirect


def management_root(request, instance_url_name):
    return redirect('calendars', instance_url_name=instance_url_name)


def calendar_info(request, instance):
    return {
        'instance': instance
    }


def calendar_info_validator(field_name, value, model_name):
    return None


def upcoming_events_info(request, instance):
    return {
        'instance': instance
    }


def upcoming_events_info_validator(field_name, value, model_name):
    return None
