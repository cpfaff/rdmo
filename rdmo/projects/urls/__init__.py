from django.urls import re_path

from ..views import (IntegrationCreateView, IntegrationDeleteView,
                     IntegrationUpdateView, IntegrationWebhookView,
                     InviteDeleteView, IssueDetailView, IssueSendView,
                     IssueUpdateView, MembershipCreateView,
                     MembershipDeleteView, MembershipUpdateView,
                     ProjectAnswersExportView, ProjectAnswersView,
                     ProjectCancelView, ProjectCreateImportView,
                     ProjectCreateView, ProjectDeleteView, ProjectDetailView,
                     ProjectErrorView, ProjectExportView, ProjectJoinView,
                     ProjectLeaveView, ProjectQuestionsView, ProjectsView,
                     ProjectUpdateCatalogView, ProjectUpdateImportView,
                     ProjectUpdateInformationView, ProjectUpdateParentView,
                     ProjectUpdateTasksView, ProjectUpdateView,
                     ProjectUpdateViewsView, ProjectViewExportView,
                     ProjectViewView, SiteProjectsView, SnapshotCreateView,
                     SnapshotRollbackView, SnapshotUpdateView)

urlpatterns = [
    re_path(r'^$', ProjectsView.as_view(), name='projects'),
    re_path(r'^all/$', SiteProjectsView.as_view(), name='site_projects'),

    re_path(r'^create/$', ProjectCreateView.as_view(), name='project_create'),
    re_path(r'^join/(?P<token>.+)/$', ProjectJoinView.as_view(), name='project_join'),
    re_path(r'^cancel/(?P<token>.+)/$', ProjectCancelView.as_view(), name='project_cancel'),
    re_path(r'^import/$', ProjectCreateImportView.as_view(), name='project_create_import'),
    re_path(r'^import/(?P<format>[a-z-]+)/$', ProjectCreateImportView.as_view(), name='project_create_import'),

    re_path(r'^(?P<pk>[0-9]+)/$', ProjectDetailView.as_view(), name='project'),
    re_path(r'^(?P<pk>[0-9]+)/update/$', ProjectUpdateView.as_view(), name='project_update'),
    re_path(r'^(?P<pk>[0-9]+)/update/information/$', ProjectUpdateInformationView.as_view(), name='project_update_information'),
    re_path(r'^(?P<pk>[0-9]+)/update/catalog/$', ProjectUpdateCatalogView.as_view(), name='project_update_catalog'),
    re_path(r'^(?P<pk>[0-9]+)/update/parent/$', ProjectUpdateParentView.as_view(), name='project_update_parent'),
    re_path(r'^(?P<pk>[0-9]+)/update/tasks/$', ProjectUpdateTasksView.as_view(), name='project_update_tasks'),
    re_path(r'^(?P<pk>[0-9]+)/update/views/$', ProjectUpdateViewsView.as_view(), name='project_update_views'),
    re_path(r'^(?P<pk>[0-9]+)/delete/$', ProjectDeleteView.as_view(), name='project_delete'),
    re_path(r'^(?P<pk>[0-9]+)/leave/$', ProjectLeaveView.as_view(), name='project_leave'),
    re_path(r'^(?P<pk>[0-9]+)/export/(?P<format>[a-z-]+)/$', ProjectExportView.as_view(), name='project_export'),
    re_path(r'^(?P<pk>[0-9]+)/import/$', ProjectUpdateImportView.as_view(), name='project_update_import'),
    re_path(r'^(?P<pk>[0-9]+)/import/(?P<format>[a-z-]+)/$', ProjectUpdateImportView.as_view(), name='project_update_import'),

    re_path(r'^(?P<project_id>[0-9]+)/memberships/create/$', MembershipCreateView.as_view(), name='membership_create'),
    re_path(r'^(?P<project_id>[0-9]+)/memberships/(?P<pk>[0-9]+)/update/$', MembershipUpdateView.as_view(), name='membership_update'),
    re_path(r'^(?P<project_id>[0-9]+)/memberships/(?P<pk>[0-9]+)/delete/$', MembershipDeleteView.as_view(), name='membership_delete'),
    re_path(r'^(?P<project_id>[0-9]+)/invite/(?P<pk>[0-9]+)/delete/$', InviteDeleteView.as_view(), name='invite_delete'),

    re_path(r'^(?P<project_id>[0-9]+)/integrations/create/(?P<provider_key>[a-z]+)/$', IntegrationCreateView.as_view(), name='integration_create'),
    re_path(r'^(?P<project_id>[0-9]+)/integrations/(?P<pk>[0-9]+)/update/$', IntegrationUpdateView.as_view(), name='integration_update'),
    re_path(r'^(?P<project_id>[0-9]+)/integrations/(?P<pk>[0-9]+)/delete/$', IntegrationDeleteView.as_view(), name='integration_delete'),
    re_path(r'^(?P<project_id>[0-9]+)/integrations/(?P<pk>[0-9]+)/webhook/$', IntegrationWebhookView.as_view(), name='integration_webhook'),

    re_path(r'^(?P<project_id>[0-9]+)/issues/(?P<pk>[0-9]+)/$', IssueDetailView.as_view(), name='issue'),
    re_path(r'^(?P<project_id>[0-9]+)/issues/(?P<pk>[0-9]+)/update/$', IssueUpdateView.as_view(), name='issue_update'),
    re_path(r'^(?P<project_id>[0-9]+)/issues/(?P<pk>[0-9]+)/send/$', IssueSendView.as_view(), name='issue_send'),

    re_path(r'^(?P<project_id>[0-9]+)/snapshots/create/$', SnapshotCreateView.as_view(), name='snapshot_create'),
    re_path(r'^(?P<project_id>[0-9]+)/snapshots/(?P<pk>[0-9]+)/update/$', SnapshotUpdateView.as_view(), name='snapshot_update'),
    re_path(r'^(?P<project_id>[0-9]+)/snapshots/(?P<pk>[0-9]+)/rollback/$', SnapshotRollbackView.as_view(), name='snapshot_rollback'),

    re_path(r'^(?P<pk>[0-9]+)/answers/$', ProjectAnswersView.as_view(), name='project_answers'),
    re_path(r'^(?P<pk>[0-9]+)/answers/export/(?P<format>[a-z]+)/$', ProjectAnswersExportView.as_view(), name='project_answers_export'),

    re_path(r'^(?P<pk>[0-9]+)/snapshots/(?P<snapshot_id>[0-9]+)/answers/$', ProjectAnswersView.as_view(), name='project_answers'),
    re_path(r'^(?P<pk>[0-9]+)/snapshots/(?P<snapshot_id>[0-9]+)/answers/export/(?P<format>[a-z]+)/$', ProjectAnswersExportView.as_view(), name='project_answers_export'),

    re_path(r'^(?P<pk>[0-9]+)/views/(?P<view_id>[0-9]+)/$', ProjectViewView.as_view(), name='project_view'),
    re_path(r'^(?P<pk>[0-9]+)/views/(?P<view_id>[0-9]+)/export/(?P<format>[a-z]+)/$', ProjectViewExportView.as_view(), name='project_view_export'),

    re_path(r'^(?P<pk>[0-9]+)/snapshots/(?P<snapshot_id>[0-9]+)/views/(?P<view_id>[0-9]+)/$', ProjectViewView.as_view(), name='project_view'),
    re_path(r'^(?P<pk>[0-9]+)/snapshots/(?P<snapshot_id>[0-9]+)/views/(?P<view_id>[0-9]+)/export/(?P<format>[a-z]+)/$', ProjectViewExportView.as_view(), name='project_view_export'),

    re_path(r'^(?P<pk>[0-9]+)/questions/', ProjectQuestionsView.as_view(), name='project_questions'),
    re_path(r'^(?P<pk>[0-9]+)/error/', ProjectErrorView.as_view(), name='project_error'),
]
