# -*- coding: utf-8 -*-




from django.urls import re_path

from importer import routes

_type_pattern = '(?P<import_type>(species|tree))'
_ie_pattern = '(?P<import_event_id>\d+)'
_import_api_pattern = _type_pattern + '/' + _ie_pattern


urlpatterns = [
    re_path(r'^$', routes.list_imports, name='list_imports'),
    re_path(r'^table/(?P<table_name>\w+)/$', routes.get_import_table,
        name='get_import_table'),
    re_path(r'^start_import/$', routes.start_import, name='start_import'),
    re_path(r'^status/%s/' % _import_api_pattern, routes.show_import_status,
        name='status'),
    re_path(r'^cancel/%s/$' % _import_api_pattern, routes.cancel, name='cancel'),
    re_path(r'^species/solve(?P<import_event_id>\d+)/(?P<row_index>\d+)/$',
        routes.solve, name='solve'),
    re_path(r'^update/%s/(?P<row_id>\d+)/$' % _type_pattern,
        routes.update_row, name='update_row'),
    re_path(r'^commit/%s/$' % _import_api_pattern, routes.commit, name='commit'),

    re_path(r'^export/species/all', routes.export_all_species,
        name='export_all_species'),
    re_path(r'^export/%s/$' % _import_api_pattern, routes.export_single_import,
        name='export_single_import'),
    re_path(r'^download_template/%s/$' % _type_pattern,
        routes.download_import_template,
        name='download_import_template'),

    # API
    re_path(r'^api/merge$', routes.merge_species, name='merge'),
]
