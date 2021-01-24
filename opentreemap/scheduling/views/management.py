# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import locale
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator, validate_email
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from scheduling.views import update_instance_fields
from opentreemap.util import json_from_request, dotted_split
from otm_comments.views import get_comments
from treemap.lib.external_link import (get_url_tokens_for_display,
                                       validate_token_template)
from treemap.models import BenefitCurrencyConversion, Plot, Tree
from treemap.units import get_value_display_attr, get_convertible_units, \
    get_unit_name
from treemap.util import package_field_errors


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