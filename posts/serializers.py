from rest_framework import serializers
from .models import User, Post, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'created_at']
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not self.context.get('is_admin', False):
            # Hide email from non-admin users
            representation.pop('email', None)
        return representation


class PostSerializer(serializers.ModelSerializer):
    comments = serializers.StringRelatedField(many=True, read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'comments']
        read_only_fields = ['id', 'author', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not self.context.get('is_admin', False):
            # Hide author details from non-admin users
            representation['author'] = 'Anonymous' if not instance.author else instance.author.username
        return representation


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'created_at']
        read_only_fields = ['id', 'author', 'post', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not self.context.get('is_admin', False):
            # Hide author details from non-admin users
            representation['author'] = 'Anonymous' if not instance.author else instance.author.username
        return representation

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value

    def validate_author(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value
