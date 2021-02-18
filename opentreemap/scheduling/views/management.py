# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.shortcuts import redirect
from django.views.decorators.http import require_POST 
import dateutil.parser
from schedule.models import Event, Calendar, Rule
from schedule.utils import (
    check_calendar_permissions,
)
from django.http import JsonResponse
from treemap.models import Tree
import rollbar

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
    tree_id = request.POST.get("treeId")
    color_event = request.POST.get("eventColor")
    frequency = request.POST.get("frequency")
    repeat_until = request.POST.get("repeat")
    
    act_plot_id=Tree.objects.get(pk=tree_id).plot.id

    if (color_event == "white"):
        color_event = '#ffffff'
    elif (color_event == "black"):
        color_event = '#000000'

    response_data = _api_create_event(start, end, calendar_slug, title,
                    description, act_plot_id, color_event, frequency, repeat_until)
    return JsonResponse(response_data)

def _api_create_event(start, end, calendar_slug, title, description, plot_id,
                      color_event, frequency, repeat_until):
    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)
    rule = None
    event_freq = frequency

    if event_freq == "" or event_freq == "Once":
        event_freq = None
    if event_freq is not None:
        rule = Rule.objects.get(name=event_freq)
    calendar = Calendar.objects.get(slug=calendar_slug)
    if (plot_id is None):
        plot_id = ''
    if (color_event is None and color_event is not ""):
        color_event = '#000000'
    if rule:
        Event.objects.create(
            start=start, end=end, title=title, calendar=calendar,
            description=description, plot_id=plot_id, color_event=color_event,
            rule=rule, end_recurring_period=repeat_until
        )
    else:
        Event.objects.create(
            start=start, end=end, title=title, calendar=calendar,
            description=description, plot_id=plot_id, color_event=color_event,
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
    plot_id = request.POST.get("plotId")
    color_event = request.POST.get("eventColor")
    frequency = request.POST.get("frequency")
    repeat_until = request.POST.get("repeat")

    if (color_event == "white"):
        color_event = '#ffffff'
    elif (color_event == "black"):
        color_event = '#000000'

    response_data = _api_edit_event(start, end, title, description,
        primary_key, plot_id, color_event, frequency, repeat_until)
    return JsonResponse(response_data)

def _api_edit_event(start, end, title, description, primary_key, plot_id,
    color_event, frequency, repeat_until):
    event = Event.objects.get(pk=primary_key)
    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)
    event_rule = None
    event_freq = frequency
    
    #occurrence = Event.objects.get(pk=primary_key).get_occurrence(start.replace(tzinfo=None))
    # event = occurrence.event
    #rollbar.report_message('occurrence found: ', 'warning', occurrence)
    # rollbar.report_message('occurrence event found: ', 'warning', event)

    if event_freq == "" or event_freq == "Once":
        event_freq = None

    if event_freq is not None:
        event_rule = Rule.objects.get(name=event_freq)
    if repeat_until is "":
        repeat_until = None
    if (plot_id is None):
        plot_id = ''
    if (color_event is None and color_event is not ""):
        color_event = '#000000'
    
    event.plot_id = plot_id
    event.start = start
    event.end = end
    event.title = title
    event.description = description
    event.color_event = color_event
    event.rule = event_rule
    event.end_recurring_period=repeat_until
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

