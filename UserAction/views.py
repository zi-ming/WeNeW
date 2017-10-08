from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth import login, logout
from UserAction.models import *


def userlogin(req):
    errors = []
    if req.method == "POST":
        try:
            username = req.POST.get("username","")
            password = req.POST.get("password", "")
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(req, user)
                response = HttpResponseRedirect(req.GET.get('next') or '/news/')
                return response
            elif user is None:
                errors.append(u'用户名或密码错误!')
            elif user.is_active:
                errors.append(u'该用户已被冻结!')
        except Exception as e:
            errors.append(str(e))
    return render(req, "UserAction/login.html", {"errors": errors})


def userlogout(req):
    logout(req)
    response = HttpResponseRedirect(req.GET.get('next') or "/news/")
    return response


def register(req):
    errors = []
    if req.method == "POST":
        try:
            username = req.POST.get("username")
            password = req.POST.get("password")
            if User.objects.filter(username=username).count()==0:
                user = User()
                user.username = username
                user.set_password(password)
                user.save()
                return HttpResponseRedirect("/user/login")
            else:
                errors.append("该用户已存在.")
        except Exception as e:
            errors.append(str(e))
    return render(req, "UserAction/register.html", {"errors": errors})
