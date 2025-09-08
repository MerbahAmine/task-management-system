# apps/tasks/serializers.py
from rest_framework import serializers
from .models import Task, Tag, Comment, TaskAssignment, TaskHistory
from django.contrib.auth import get_user_model

User = get_user_model()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    assigned_to = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    created_by = serializers.ReadOnlyField(source='created_by.id')

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'is_archived']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        assigned_users = validated_data.pop('assigned_to', [])
        task = Task.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            task.tags.add(tag)
        task.assigned_to.set(assigned_users)
        return task

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        assigned_users = validated_data.pop('assigned_to', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tags_data is not None:
            instance.tags.clear()
            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(**tag_data)
                instance.tags.add(tag)
        if assigned_users is not None:
            instance.assigned_to.set(assigned_users)
        instance.save()
        return instance

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Comment
        fields = ['id', 'task', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class TaskHistorySerializer(serializers.ModelSerializer):
    changed_by = serializers.ReadOnlyField(source='changed_by.id')

    class Meta:
        model = TaskHistory
        fields = '__all__'
