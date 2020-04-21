from django.contrib.auth.models import User
from rest_framework import serializers

from posts.models import Post, Comment, Group, Follow


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ('author', 'pub_date',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('author', 'created', 'post',)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'title',)
        model = Group


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username', read_only=True)
    following = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        fields = '__all__'
        model = Follow
        read_only_fields = ('user',)

    def validate_following(self, value):
        user = self.context['request'].user
        if Follow.objects.filter(user=user, following__username=value).exists():
            raise serializers.ValidationError("Following already exists")
        if user.username == value:
            raise serializers.ValidationError("You can't follow to yourself")
        return value
