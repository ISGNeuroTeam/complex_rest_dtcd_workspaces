from rest_framework import serializers
from dtcd_workspaces.workspaces.directory_content import DirectoryContent
from dtcd_workspaces.workspaces.workspace import Workspace
from dtcd_workspaces.workspaces.directory import Directory


class DirectoryContentSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=2048)
    creation_time = serializers.FloatField(read_only=True)
    modification_time = serializers.FloatField(read_only=True)
    meta = serializers.DictField()

    class Meta:
        read_only_fields = ('creation_time', 'modification_time')


class DirectorySerializer(DirectoryContentSerializer):
    def create(self, validated_data):
        directory = Directory(validated_data['path'])
        directory.meta = validated_data['meta']
        directory.save()
        return directory

    def update(self, instance, validated_data):
        instance.meta = validated_data.get('meta', instance.meta)
        instance.save()
        return instance


class WorkspaceSerializer(DirectoryContentSerializer):
    content = serializers.DictField()

    def create(self, validated_data):
        workspace = Workspace(validated_data['path'])
        workspace.meta = validated_data['meta']
        workspace.content = validated_data['content']
        workspace.save()
        return workspace

    def update(self, instance, validated_data):
        instance.meta = validated_data.get('meta', instance.meta)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance







