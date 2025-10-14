# -*- coding: UTF-8 -*-
__author__ = "余洋"
__doc__ = "abstracts"
"""
  * @File    :   abstracts.py
  * @Time    :   2023/05/04 11:53:28
  * @Author  :   余洋
  * @Version :   1.0
  * @Contact :   yuyangit.0515@qq.com
  * @License :   (C)Copyright 2019-2023, 希洋 (Ship of Ocean)
  * @Desc    :   None
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from random import randint
from datetime import datetime
import pytz
from django.conf import settings
from xy_django_model.model import gen_upload_to


class MAEmailCredential(models.Model):
    id = models.BigAutoField(primary_key=True)

    email_address = models.CharField(
        verbose_name=_("邮箱"),
        max_length=255,
        blank=True,
        null=True,
    )
    email_password = models.CharField(
        verbose_name=_("邮箱密码"),
        max_length=255,
        blank=True,
        null=True,
    )
    email_host = models.CharField(
        verbose_name=_("邮箱主机地址"),
        max_length=255,
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("是否启用"),
        default=True,
    )

    class Meta:
        abstract = True
        verbose_name = _("邮箱凭证")
        verbose_name_plural = _("邮箱凭证")

    def __str__(self):
        return f"{self.id}. {self.email_address}"


class MACaptcha(models.Model):
    id = models.BigAutoField(primary_key=True)

    code = models.CharField(
        verbose_name=_("验证码"),
        max_length=255,
        unique=True,
        blank=False,
        null=True,
        default="",
    )
    create_at = models.DateTimeField(
        verbose_name=_("创建时间"),
        auto_now_add=True,
        blank=True,
        null=True,
    )
    signature = models.CharField(
        verbose_name=_("标签"),
        max_length=255,
        unique=True,
        blank=True,
        null=True,
    )

    @classmethod
    def generate_new_captcha(
        cls,
        mode_list=["all"],
        length=4,
    ):
        num_list = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
        ]
        lower_alpha_list = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
        ]
        uppper_alpha_list = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]
        source_list = []
        for mode in mode_list:
            if mode == "num":
                source_list += num_list
            elif mode == "lower":
                source_list += lower_alpha_list
            elif mode == "upper":
                source_list += uppper_alpha_list
            else:
                source_list += num_list
                source_list += lower_alpha_list
                source_list += uppper_alpha_list

        captcha = ""
        if length <= len(source_list):
            for i in range(length):
                captcha += source_list[randint(0, len(source_list) - 1)]

        return captcha

    def validate(self):
        OVER_TIME_SECONDS = 60
        utc = pytz.UTC
        now = utc.localize(datetime.now())
        return (now - self.create_at).total_seconds() > OVER_TIME_SECONDS

    class Meta:
        abstract = True
        verbose_name = _("验证码")
        verbose_name_plural = _("验证码")

    def __str__(self):
        return f"{self.id}. {self.code}"


class MASMSCaptchaCredential(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        verbose_name=_("平台名称"),
        max_length=255,
        blank=True,
        null=True,
    )
    app_id = models.CharField(
        verbose_name=_("app_id"),
        max_length=255,
        blank=True,
        null=True,
    )
    app_key = models.CharField(
        verbose_name=_("app_key"),
        max_length=255,
        blank=True,
        null=True,
    )
    app_secret = models.CharField(
        verbose_name=_("app_secret"),
        max_length=255,
        blank=True,
        null=True,
    )
    template_id = models.IntegerField(
        verbose_name=_("模板ID"),
        blank=True,
        null=True,
    )
    sign = models.CharField(
        verbose_name=_("签名"),
        max_length=255,
        blank=True,
        null=True,
    )
    options_config = models.TextField(
        verbose_name=_("其他配置"),
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True
        verbose_name = _("短信凭证")
        verbose_name_plural = _("短信凭证")

    def __str__(self):
        return f"{self.id}. {self.name}"


@gen_upload_to
def user__thumbnails(*args, **kwargs):
    pass


class MASiteUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    date_of_birth = models.DateTimeField(
        verbose_name=_("生日"),
        auto_now=True,
        editable=True,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("是否启用"),
        default=True,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    # 性别选择
    sex_choices = (
        ("man", _("男")),
        ("female", _("女")),
        ("unknown", _("未知")),
    )
    # 必须
    email = models.EmailField(
        verbose_name=_("邮箱"),
        max_length=255,
        blank=True,
        null=True,
    )
    mobile = models.CharField(
        verbose_name=_("手机号"),
        max_length=255,
        blank=True,
        null=True,
    )
    username = models.CharField(
        verbose_name=_("用户名"),
        max_length=255,
        default="",
        blank=True,
        null=True,
    )
    name = models.CharField(
        verbose_name=_("姓名"),
        max_length=255,
        default="",
        blank=True,
        null=True,
    )
    password = models.CharField(
        verbose_name=_("密码"),
        max_length=255,
        default="",
        blank=True,
        null=True,
    )
    sex = models.CharField(
        verbose_name=_("性别"),
        default="unknown",
        choices=sex_choices,
        blank=True,
        null=True,
        max_length=15,
    )
    thumb = models.ImageField(
        verbose_name=_("头像"),
        upload_to=user__thumbnails,
        default="",
        blank=True,
        null=True,
    )
    age = models.IntegerField(
        verbose_name=_("年龄"),
        default=0,
        blank=True,
        null=True,
    )
    expires_time = models.DateTimeField(
        verbose_name=_("登陆过期时间"),
        auto_now_add=True,
        blank=True,
        null=True,
    )
    nickname = models.CharField(
        verbose_name=_("昵称"),
        max_length=255,
        default="",
        blank=True,
        null=True,
    )
    userid = models.UUIDField(
        verbose_name=_("用户ID"),
        default=uuid.uuid4,
        editable=True,
        unique=True,
        blank=True,
        null=True,
    )
    token = models.UUIDField(
        verbose_name=_("token"),
        default=uuid.uuid4,
        editable=True,
        unique=True,
        blank=True,
        null=True,
    )
    validation_token = models.UUIDField(
        verbose_name=_("验证token"),
        default=uuid.uuid4,
        editable=True,
        unique=True,
        blank=True,
        null=True,
    )
    validation_expires_time = models.DateTimeField(
        verbose_name=_("验证过期时间"),
        auto_now_add=True,
        blank=True,
        null=True,
    )
    idcard_no = models.CharField(
        verbose_name=_("身份证号"),
        max_length=255,
        null=True,
        blank=True,
    )
    debug = True

    @property
    def thumb_url(self):
        if bool(self.thumb) is True:
            protocol = "https"
            if self.debug is True:
                protocol = "http"
            if hasattr(settings, "PROTOCOL"):
                protocol = settings.PROTOCOL
            return f"{protocol}://{settings.DOMAIN}{self.thumb.url}"
        return None

    @classmethod
    def login_validate(cls, mobile="", password=""):
        validate = (
            mobile is not None
            and mobile != ""
            and password is not None
            and password != ""
        )
        if validate is True:
            validate = cls.objects.exists(
                mobile=mobile,
                password=password,
            )
        return validate

    def login(self):
        self.token = uuid.uuid4()
        self.save()

    @classmethod
    def register_validate(
        cls,
        mobile="",
        password="",
        *args,
        **kwargs,
    ):
        validate = (
            mobile is not None
            and mobile != ""
            and password is not None
            and password != ""
        )
        if validate is True:
            validate = cls.objects.filter(mobile=mobile, password=password).count() == 0
        return validate

    @classmethod
    def email_register_validate(
        cls,
        email="",
        password="",
        *args,
        **kwargs,
    ):
        validate = (
            email is not None
            and email != ""
            and password is not None
            and password != ""
        )
        if validate is True:
            validate = cls.objects.filter(email=email, password=password).count() == 0
        return validate

    @classmethod
    def sms_register_validate(
        cls,
        mobile="",
        password="",
        *args,
        **kwargs,
    ):
        validate = (
            mobile is not None
            and mobile != ""
            and password is not None
            and password != ""
        )
        if validate is True:
            validate = cls.objects.filter(mobile=mobile, password=password).count() == 0
        return validate

    class Meta:
        abstract = True
        verbose_name = _("站点用户")
        verbose_name_plural = _("站点用户")

    def __str__(self):
        return f"{self.id}. {self.username}"


class MAAuthUserCredential(models.Model):
    id = models.BigAutoField(primary_key=True)

    platform = models.CharField(
        verbose_name=_("平台名称"),
        max_length=255,
        null=True,
        blank=True,
    )
    open_id = models.CharField(
        verbose_name=_("open_id"),
        max_length=255,
        null=True,
        blank=True,
    )
    union_id = models.CharField(
        verbose_name=_("union_id"),
        max_length=255,
        null=True,
        blank=True,
    )
    app_key = models.CharField(
        verbose_name=_("app_key"),
        max_length=255,
        null=True,
        blank=True,
    )
    app_secret = models.CharField(
        verbose_name=_("app_secret"),
        max_length=255,
        null=True,
        blank=True,
    )
    mobile = models.CharField(
        verbose_name=_("手机号"),
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
        verbose_name = _("授权用户凭证")
        verbose_name_plural = _("授权用户凭证")

    def __str__(self):
        return f"{self.id}. {self.platform}"


class MAAuthUser(MASiteUser):
    platform_userid = models.CharField(
        verbose_name=_("平台用户id"),
        max_length=255,
        unique=True,
    )
    user_secret = models.CharField(
        verbose_name=_("平台用户密钥"),
        max_length=255,
        unique=True,
    )
    auth_token = models.CharField(
        verbose_name=_("token"),
        max_length=255,
        unique=True,
    )
    refresh_token = models.CharField(
        verbose_name=_("refresh_token"),
        max_length=255,
        unique=True,
    )
    openid = models.CharField(
        verbose_name=_("openid"),
        max_length=255,
        unique=True,
    )
    appid = models.CharField(
        verbose_name=_("appid"),
        max_length=255,
        unique=True,
    )
    identifier = models.UUIDField(
        verbose_name=_("唯一标识"),
        null=True,
        blank=True,
        default=uuid.uuid4,
        editable=True,
        unique=True,
    )

    class Meta:
        abstract = True
        verbose_name = _("第三方平台用户")
        verbose_name_plural = _("第三方平台用户")

    def __str__(self):
        return f"{self.id}. {self.identifier}"
