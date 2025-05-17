from django.contrib import admin
from .models import Category, Transaction, Goal

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'type')
    list_filter  = ('type',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'amount', 'timestamp')

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'name', 
        'target_amount', 'start_date', 
        'end_date', 'frequency'
    )
    list_filter  = ('frequency',)
