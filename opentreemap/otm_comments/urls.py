# -*- coding: utf-8 -*-




from django.urls import re_path

from otm_comments.views import (comments_csv_endpoint, flag_endpoint,
                                unflag_endpoint, hide_flags_endpoint,
                                archive_endpoint, unarchive_endpoint,
                                hide_endpoint, show_endpoint,
                                comment_moderation_partial_endpoint)

urlpatterns = [
    re_path(r'^(?P<comment_id>\d+)/flag/$', flag_endpoint, name='flag-comment'),
    re_path(r'^(?P<comment_id>\d+)/unflag/$', unflag_endpoint,
        name='unflag-comment'),
    re_path(r'^hide-flags/$', hide_flags_endpoint, name='hide-comment-flags'),
    re_path(r'^archive/$', archive_endpoint, name='archive-comments'),
    re_path(r'^unarchive/$', unarchive_endpoint, name='unarchive-comments'),
    re_path(r'^hide/$', hide_endpoint, name='hide-comments'),
    re_path(r'^show/$', show_endpoint, name='show-comments'),
    re_path(r'^csv/$', comments_csv_endpoint, name='comments-csv'),
    re_path(r'^moderation-table/$', comment_moderation_partial_endpoint,
        name='comment_moderation')
]
