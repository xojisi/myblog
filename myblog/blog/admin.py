# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import User,Tag,Article,Category,Comment,Links,Ad

# Register your models here.

class ArticleAdmin(admin.ModelAdmin):

    # 查看时的列显示项目设置
    list_display = ('title','desc','click_count',)
    # 查看时,设置点击后可进行详细页跳转
    list_display_links = ('desc', )
    # 查看时,可以编辑      (注意:不能同时属于可点击又可以编辑)
    list_editable = ('click_count',)

    # 增加时,除了定义的项目,其他全部显示
    # exclude = ('title','desc','content',)

    # 增加时,仅显示定义的项目
    # fields = ('title','desc','content',)

    # 增加时,以可收缩的高级设置呈现
    fieldsets = (
        (None, {
            'fields': ('title', 'desc', 'content','user','category','tag',)
        }),
        ('高级设置', {
            'classes': ('collapse',),
            'fields': ('click_count', 'is_recommend',),
        }),
    )

    # 引入富文本编辑器
    class Media:
        js = (
            '/static/js/kindeditor/kindeditor-all.js',
            '/static/js/kindeditor/lang/zh-CN.js',
            '/static/js/kindeditor/config.js',
        )

class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'index',)
    list_editable = ('index',)

admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Article,ArticleAdmin)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Links)
admin.site.register(Ad,AdAdmin)
