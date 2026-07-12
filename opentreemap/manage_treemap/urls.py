



from django.urls import re_path

from manage_treemap import routes

urlpatterns = [
    re_path(r'^$', routes.management, name='management'),
    re_path(r'^notifications/$', routes.admin_counts, name='admin_counts'),

    re_path(r'^site-config/$', routes.site_config, name='site_config'),
    re_path(r'^external-link/$', routes.external_link, name='external_link'),
    re_path(r'^branding/$', routes.branding, name='branding'),
    re_path(r'^embed/$', routes.embed, name='embed'),
    re_path(r'^logo/$', routes.update_logo, name='logo_endpoint'),
    re_path(r'^green-infrastructure/$', routes.green_infrastructure,
        name='green_infrastructure'),

    re_path(r'^comment-moderation/$', routes.comment_moderation,
        name='comment_moderation_admin'),

    re_path(r'^photo-review/$', routes.photo_review_admin,
        name='photo_review_admin'),
    re_path(r'^photo_review-partial/$', routes.photo_review,
        name='photo_review_partial'),
    re_path(r'^photo-review/approve-reject/(?P<action>(approve)|(reject))$',
        routes.approve_or_reject_photos, name='approve_or_reject_photos'),

    re_path(r'^user-roles/$', routes.user_roles, name='user_roles'),
    re_path(r'^user-roles-partial/$', routes.user_roles_partial,
        name='user_roles_partial'),
    re_path(r'^user-invite/(?P<invite_id>\d+)$', routes.user_invites,
        name='user_invite'),
    re_path(r'^roles/$', routes.roles, name='roles_endpoint'),
    re_path(r'^export/user/(?P<data_format>(csv|json))/$',
        routes.begin_export_users, name='management_begin_export_users'),
    re_path(r'^clear-udf-notifications/$',
        routes.clear_udf_notifications, name='clear_udf_notifications'),

    re_path(r'^bulk-uploader/$', routes.importer, name='importer'),
    re_path(r'^benefits/$', routes.benefits, name='benefits'),
    re_path(r'^units/$', routes.units, name='units_endpoint'),

    re_path(r'^udfs/$', routes.udfs, name='udfs'),
    re_path(r'^udfs/(?P<udf_id>\d+)$', routes.udf_change, name='udfs_change'),
    re_path(r'^search-configuration/$', routes.search_config_page,
        name='search_config_admin'),
    re_path(r'^search-configuration-partial/$', routes.search_config,
        name='search_config'),
    re_path(r'^field-configuration/$', routes.field_configs,
        name='field_configs'),
    re_path(r'^set-fields/$', routes.set_field_configs,
        name='set_field_configs'),
]
