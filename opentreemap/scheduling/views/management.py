# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.shortcuts import redirect
from django.views.decorators.http import require_POST 
import dateutil.parser
from schedule.models import Event, Calendar
from schedule.utils import (
    check_calendar_permissions,
)
from django.http import JsonResponse

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


@require_POST
@check_calendar_permissions
def api_create_event(request, **kwargs):
    response_data = {}
    start = request.POST.get("start")
    end = request.POST.get("end")
    title = request.POST.get("title")
    description = request.POST.get("description")
    calendar_slug = request.POST.get("calendar")

    response_data = _api_create_event(start, end, calendar_slug, title, description)
    return JsonResponse(response_data)

def _api_create_event(start, end, calendar_slug, title, description):
    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)
    calendar = Calendar.objects.get(slug=calendar_slug)

    Event.objects.create(
        start=start, end=end, title=title, calendar=calendar,
        description=description
    )

    response_data = {}
    response_data["status"] = "OK"
    return response_data

@require_POST
@check_calendar_permissions
def api_edit_event(request, **kwargs):
    response_data = {}
    start = request.POST.get("start")
    end = request.POST.get("end")
    title = request.POST.get("title")
    description = request.POST.get("description")
    primary_key = request.POST.get("primaryKey")

    response_data = _api_edit_event(start, end, calendar_slug, title, description, primary_key)
    return JsonResponse(response_data)

def _api_edit_event(start, end, calendar_slug, title, description, primary_key):
    event = Event.objects.get(pk=primary_key)
    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)

    event.start = start
    event.end = end
    event.title = title
    event.description = description
    event.save()

    response_data = {}
    response_data["status"] = "OK"
    return response_data

@require_POST
@check_calendar_permissions
def api_delete_event(request, **kwargs):
    response_data = {}
    event_id = request.POST.get("eventId")
    response_data = _api_delete_event(event_id)
    return JsonResponse(response_data)

def _api_delete_event(event_id):
    Event.objects.get(pk=event_id).delete()

    response_data = {}
    response_data["status"] = "OK"
    return response_data