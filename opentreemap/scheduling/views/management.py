# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.db.models import Q

import dateutil.parser
import dateutil.tz
from schedule.models import Event, Calendar, Rule, Occurrence
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
    occ_created = request.POST.get("occCreated")
    act_plot_id = None
    
    if tree_id is not None:
        act_plot_id=Tree.objects.get(pk=tree_id).plot.id

    if (color_event == "white"):
        color_event = '#ffffff'
    elif (color_event == "black"):
        color_event = '#000000'

    response_data = _api_create_event(start, end, calendar_slug, title,
                    description, act_plot_id, color_event, frequency, 
                    repeat_until, tree_id, occ_created)
    return JsonResponse(response_data)

def _api_create_event(start, end, calendar_slug, title, description, plot_id,
                      color_event, frequency, repeat_until, tree_id,
                      occ_created):
    start = dateutil.parser.parse(start.replace('Z',''))
    end = dateutil.parser.parse(end.replace('Z',''))
    #start = dateutil.parser.parse(start)
    #end = dateutil.parser.parse(end)
    rule = None
    evt = None
    event_freq = frequency

    if event_freq == "" or event_freq == "Once":
        event_freq = None
    if event_freq is not None:
        rule = Rule.objects.get(name=event_freq)
    calendar = Calendar.objects.get(slug=calendar_slug)
    if (plot_id is None):
        plot_id = ''
    if (tree_id is None):
        tree_id = ''
    if (color_event is None and color_event is not ""):
        color_event = '#000000'
    if rule:
        repeat_until = dateutil.parser.parse(repeat_until.replace('Z',''))
        evt = Event(
            start=start, end=end, title=title, calendar=calendar,
            description=description, plot_id=plot_id, color_event=color_event,
            rule=rule, end_recurring_period=repeat_until, tree_id=tree_id
        )
        occs = evt.get_occurrences(start, repeat_until)
    else:
        evt = Event(
            start=start, end=end, title=title, calendar=calendar,
            description=description, plot_id=plot_id, color_event=color_event,
            tree_id=tree_id
        )
        occs = evt.get_occurrences(start, end)
    

    for occurrence in occs:
        Occurrence.objects.create(
            occ_created=occ_created,
            title=title,
            description=description,
            start=occurrence.start,
            end=occurrence.end,
            original_start=evt.start,
            original_end=evt.end,
            plot_id=plot_id,
            tree_id=tree_id,
            color_event=color_event,
            calendar=calendar
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
    tree_id = request.POST.get("treeId")
    color_event = request.POST.get("eventColor")
    frequency = request.POST.get("frequency")
    repeat_until = request.POST.get("repeat")
    occ_created = request.POST.get("occCreated")
    act_plot_id=None
 
    if tree_id is not None and tree_id != '':
        act_plot_id=Tree.objects.get(pk=tree_id).plot.id

    if (color_event == "white"):
        color_event = '#ffffff'
    elif (color_event == "black"):
        color_event = '#000000'

    response_data = _api_edit_event(start, end, title, description,
        primary_key, act_plot_id, color_event, frequency, repeat_until,
        tree_id, occ_created)
    return JsonResponse(response_data)

def _api_edit_event(start, end, title, description, primary_key, plot_id,
    color_event, frequency, repeat_until, tree_id, occ_created):
    edited_occurrence = Occurrence.objects.get(pk=primary_key)
    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)
    occurrences = Occurrence.objects.all().filter(Q(occ_created__iexact=occ_created))

    if (plot_id is None):
        plot_id = ''

    if (tree_id is None):
        tree_id = ''

    if (color_event is None and color_event is not ""):
        color_event = '#000000'

    for occurrence in occurrences:
        occurrence.tree_id = tree_id
        occurrence.plot_id = plot_id
        occurrence.title = title
        occurrence.description = description
        occurrence.color_event = color_event
        occurrence.save()

    edited_occurrence.start = start
    edited_occurrence.end = end
    edited_occurrence.tree_id = tree_id
    edited_occurrence.plot_id = plot_id
    edited_occurrence.title = title
    edited_occurrence.description = description
    edited_occurrence.color_event = color_event
    edited_occurrence.save()
        
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
    Occurrence.objects.get(pk=event_id).delete()

    response_data = {}
    response_data["status"] = "OK"
    return response_data

@require_POST
@check_calendar_permissions
def api_delete_all_events(request, **kwargs):
    response_data = {}
    occ_created = request.POST.get("occCreated")
    response_data = _api_delete_all_events(occ_created)
    return JsonResponse(response_data)

def _api_delete_all_events(occ_created):
    # Occurrence.objects.get(pk=event_id).delete()
    occurrences = Occurrence.objects.all().filter(Q(occ_created__iexact=occ_created))

    for occurrence in occurrences:
        occurrence.delete()

    response_data = {}
    response_data["status"] = "OK"
    return response_data
