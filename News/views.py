import json

from django.shortcuts import render,HttpResponse
from django.contrib.auth.decorators import login_required
from News import db_operation


@login_required
def news(req):
    """
    @summary: 获取新闻
    """
    if req.method == "GET":
        type = req.GET.get("type")
        latest_id = req.GET.get('id')
        user_id = req.user.is_anonymous and -1 or req.user.id

        if not type or not latest_id:
            records = db_operation.readNewList(user_id, -1, "getnew", 10)
            return render(req, "News/Blog_list.html", {'records': records})

        if type == "getcount":
            records = db_operation.readNewList(user_id, latest_id, type, 10)
            return HttpResponse(records)
        elif type in ["getnew", "getold"]:
            records = db_operation.readNewList(user_id, latest_id, type, 10)
            return HttpResponse(json.dumps([record.parseDict() for record in records]))


def content(req, id):
    """
    @summary: 读取新闻内容
    :param id: 新闻id
    """
    record = db_operation.readContent(id)
    return render(req, "News/Blog_content.html", {'record': record})
