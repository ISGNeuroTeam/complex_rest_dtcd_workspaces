from .views.workspaceview import WorkspaceView
from .views.directoryview import DirectoryView
from django.urls import re_path


app_name = 'dtcd_workspaces'
urlpatterns = [
    re_path(r'workspace/object/(?P<workspace_path>[a-zA-Z0-9_=\-]+)?$', WorkspaceView.as_view()),
    re_path(r'workspace/?$', WorkspaceView.as_view()),
    re_path(r'directory/?$', DirectoryView)
]
