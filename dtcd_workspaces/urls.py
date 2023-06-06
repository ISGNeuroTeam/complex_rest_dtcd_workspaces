from .views.workspaceview import WorkspaceView
from .views.directoryview import DirectoryView
from django.urls import re_path


urlpatterns = [
    re_path(r'workspace/?$', WorkspaceView.as_view()),
    re_path(r'directory/?$', DirectoryView.as_view())
]
