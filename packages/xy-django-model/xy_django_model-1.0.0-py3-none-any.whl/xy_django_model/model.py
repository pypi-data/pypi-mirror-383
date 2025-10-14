# -*- coding: UTF-8 -*-
__author__ = "余洋"
__doc__ = "model"
"""
  * @File    :   model.py
  * @Time    :   2023/04/27 21:07:47
  * @Author  :   余洋
  * @Version :   1.0
  * @Contact :   yuyangit.0515@qq.com
  * @License :   (C)Copyright 2019-2023, Ship of Ocean
  * @Desc    :   None
"""

from django.contrib.contenttypes.models import ContentType
import os
from functools import wraps

# Example:
# def content_file_name(instance, filename):
#     return "/".join(["content", instance.user.username, filename])


# class Content(models.Model):
#     name = models.CharField(max_length=200)
#     user = models.ForeignKey(User)
#     file = models.FileField(upload_to=content_file_name)


def default_upload_to(instance, path, filename):
    if path == None:
        path = ""
    # 文件将要上传到 <app_label>/<模型类名称>/
    return f"{ContentType.objects.get_for_model(instance).app_label}/{instance.__class__.__name__}{path}/{filename}"


def gen_upload_to(func):
    path = ""
    if func:
        path = os.path.join("/", "/".join(func.__name__.split("__")))

    @wraps(func)
    def decorated(instance, filename):
        return default_upload_to(instance=instance, path=path, filename=filename)

    return decorated


def related_name(extension="related"):
    return f"%(app_label)s_%(class)s_{extension}"
