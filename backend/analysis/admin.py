from django.contrib import admin
from .models import Insight, ChatMessage

@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'insight_type', 'created_at')
    list_filter  = ('insight_type',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'timestamp')
    list_filter  = ('role',)
