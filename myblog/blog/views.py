# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.shortcuts import render,redirect
from django.contrib.auth.hashers import make_password
from django.conf import settings
import logging
from django.db.models import Count
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from django.contrib.auth import logout, login, authenticate


from blog.models import *
from blog.forms import CommentForm,LoginForm, RegForm

logger = logging.getLogger('blog.views')
# Create your views here.
def index(request):
    # test the function of bug's log
    try:
        article_list = Article.objects.all()
        article_list = getPage(request,article_list)
        # ads_list = Ad.objects.all()
        # 文章归档
        # 1、先要去获取到文章中有的 年份-月份  2015/06文章归档
        # 使用values和distinct去掉重复数据（不可行）
        # print Article.objects.values('date_publish').distinct()
        # 直接执行原生sql呢？
        # 第一种方式（不可行）
        # archive_list =Article.objects.raw('SELECT id, DATE_FORMAT(date_publish, "%%Y-%%m") as col_date FROM blog_article ORDER BY date_publish')
        # for archive in archive_list:
        #     print archive
        # 第二种方式（不推荐）
        # cursor = connection.cursor()
        # cursor.execute("SELECT DISTINCT DATE_FORMAT(date_publish, '%Y-%m') as col_date FROM blog_article ORDER BY date_publish")
        # row = cursor.fetchall()
        # print row

    except Exception as e:
        logger.error(e)

    return render(request, 'index.html', locals())

# 全局信息
def global_setting(request):
    # 站点基本信息
    SITE_NAME = settings.SITE_NAME
    SITE_DESC = settings.SITE_DESC
    # 分类信息获取(导航数据)
    category_list = Category.objects.all()  # 可以用切片的方式，筛选数据
    # 归档信息
    archive_list = Article.objects.distinct_date()
    # 广告数据
    ads_list = Ad.objects.all()
    # 标签云
    tag_list = Tag.objects.all()
    # 友情链接
    links_list = Links.objects.all()

    # 文章排行榜
    # 浏览排行
    pageview_list = Article.objects.annotate(pageview_count=Count('click_count')).order_by('-click_count')[0:6]
    # 评论排行
    comment_count_list = Comment.objects.values('article').annotate(comment_count=Count('article')).order_by('-comment_count')
    article_comment_list = [Article.objects.get(pk=comment['article']) for comment in comment_count_list][0:6]
    return locals()

# 首页文章
def archive(request):
    try:
        # 标签筛选与文章归档用同一个模版，用一个标志区分headline
        flag = 'article'

        # 先获取客户端提交的信息
        year = request.GET.get('year',None)
        month = request.GET.get('month', None)
        # 最新文档数据

        # 用Like找
        # article_list = Article.objects.filter(date_publish__contains= year + '-' + month )

        # 用range找
        # date_from = datetime.datetime(int(year),int(month),1,0,0)
        # date_to = datetime.datetime(int(year),int(month),31,0,0)
        # article_list = Article.objects.filter(date_publish__range=(date_from,date_to))
        article_list = Article.objects.filter(date_publish__startswith=str(year)+'-'+str(month))
        article_list = getPage(request,article_list)
        # 分页器的每页数量

    except Exception as a:
        logger.error(a)

    return render(request, 'archive.html', locals())

# 标签云
def tag_cloud(request):
    try:
        # 标签筛选与文章归档用同一个模版，用一个标志区分headline
        flag = 'tag'

        # 获取客户端提交的信息
        tagid = request.GET.get('tag', None)
        Tag_id = Tag.objects.get(pk=tagid)
        Tag_name = Tag.objects.filter(pk=tagid)
        print(Tag_name)
        article_list = Tag_id.tag.all()
        article_list = getPage(request,article_list)

    except Exception as a:
            logger.error(a)
    return render(request, 'archive.html', locals())

# 分页代码
def getPage(request,article_list):
    # 分页器的每页数量
    paginator = Paginator(article_list, 8)
    try:
        page = int(request.GET.get('page', 1))
        article_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        article_list = paginator.page(1)
    return article_list

# 文章详情
def article(request):
    try:
        # 获取文章id
        id = request.GET.get('id', None)
        try:
            # 获取文章信息
            article = Article.objects.get(pk=id)
        except Article.DoesNotExist:
            return render(request, 'failure.html', {'reason': '没有找到对应的文章'})

        # 浏览量+1
        article.click_count = article.click_count + 1
        article.save()

        # 评论表单
        comment_form = CommentForm({'author': request.user.username,
                                    'email': request.user.email,
                                    'url': request.user.url,
                                    'article': id} if request.user.is_authenticated() else{'article': id})
        # 获取评论信息
        comments = Comment.objects.filter(article=article).order_by('id')
        comment_list = []
        for comment in comments:
            for item in comment_list:
                if not hasattr(item, 'children_comment'):
                    setattr(item, 'children_comment', [])
                if comment.pid == item:
                    item.children_comment.append(comment)
                    break
            if comment.pid is None:
                comment_list.append(comment)
    except Exception as e:
        print e
        logger.error(e)
    return render(request, 'article.html', locals())

# 提交评论
def comment_post(request):
    try:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            #获取表单信息
            comment = Comment.objects.create(username=comment_form.cleaned_data["author"],
                                             email=comment_form.cleaned_data["email"],
                                             url=comment_form.cleaned_data["url"],
                                             content=comment_form.cleaned_data["comment"],
                                             article_id=comment_form.cleaned_data["article"],
                                             user=request.user if request.user.is_authenticated() else None)
            comment.save()
        else:
            return render(request, 'failure.html', {'reason': comment_form.errors})
    except Exception as e:
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

# 注销
def do_logout(request):
    try:
        logout(request)
    except Exception as e:
        print e
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

# 注册
def do_reg(request):
    try:
        if request.method == 'POST':
            reg_form = RegForm(request.POST)
            if reg_form.is_valid():
                # 注册
                user = User.objects.create(username=reg_form.cleaned_data["username"],
                                    email=reg_form.cleaned_data["email"],
                                    url=reg_form.cleaned_data["url"],
                                    password=make_password(reg_form.cleaned_data["password"]),)
                user.save()

                # 登录
                user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                login(request, user)
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': reg_form.errors})
        else:
            reg_form = RegForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'reg.html', locals())

# 登录
def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                # 登录
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                    login(request, user)
                else:
                    return render(request, 'failure.html', {'reason': '登录验证失败'})
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'login.html', locals())

# 导航分类
def category(request):
    try:
        # 先获取客户端提交的信息
        cid = request.GET.get('cid', None)
        try:
            category = Category.objects.get(pk=cid)
        except Category.DoesNotExist:
            return render(request, 'failure.html', {'reason': '分类不存在'})
        article_list = Article.objects.filter(category=category)
        article_list = getPage(request, article_list)
    except Exception as e:
        logger.error(e)
    return render(request, 'category.html', locals())
