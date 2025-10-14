# -*- coding: UTF-8 -*-
__author__ = "余洋"

from django.db import models
from django.utils.translation import gettext_lazy as _
from .abstracts import (
    MAAuthUser,
    MAAuthUserCredential,
    MACaptcha,
    MAEmailCredential,
    MASiteUser,
    MASMSCaptchaCredential,
)


class MEmailCredential(MAEmailCredential):
    class Meta:
        app_label = "xy_django_app_siteuser"
        verbose_name = _("邮箱凭证")
        verbose_name_plural = _("邮箱凭证")


class MCaptcha(MACaptcha):
    class Meta:
        app_label = "xy_django_app_siteuser"
        verbose_name = _("验证码")
        verbose_name_plural = _("验证码")


class MSMSCaptchaCredential(MASMSCaptchaCredential):
    class Meta:
        app_label = "xy_django_app_siteuser"
        verbose_name = _("短信凭证")
        verbose_name_plural = _("短信凭证")


class MEmailCaptcha(MACaptcha):
    from_email = models.CharField(
        verbose_name=_("发送方邮箱"),
        max_length=255,
    )
    to_email = models.CharField(
        verbose_name=_("目标邮箱"),
        max_length=255,
    )

    class Meta:
        app_label = "xy_django_app_siteuser"
        verbose_name = _("邮箱验证码")
        verbose_name_plural = _("邮箱验证码")

    def __str__(self):
        return str(self.id) + ". " + str(self.code)


class MSMSCaptcha(MACaptcha):
    mobile = models.CharField(
        verbose_name=_("手机号"),
        max_length=255,
    )

    class Meta:
        app_label = "xy_django_app_siteuser"
        verbose_name = _("短信验证码")
        verbose_name_plural = _("短信验证码")

    def __str__(self):
        return str(self.id) + ". " + str(self.code)


class MSiteUser(MASiteUser):
    region = models.ForeignKey(
        "xy_django_app_information.MRegion",
        verbose_name=_("所在地"),
        related_name="%(app_label)s_%(class)s_region",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        app_label = "xy_django_app_siteuser"
        verbose_name = _("站点用户")
        verbose_name_plural = _("站点用户")


class MAuthUserCredential(MAAuthUserCredential):
    class Meta:
        app_label = "xy_django_app_siteuser"
        verbose_name = _("授权用户凭证")
        verbose_name_plural = _("授权用户凭证")


class MAuthUser(MAAuthUser):
    credential = models.ForeignKey(
        "xy_django_app_siteuser.MAuthUserCredential",
        verbose_name=_("授权用户凭证"),
        related_name="%(app_label)s_%(class)s_credential",
        max_length=255,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        app_label = "xy_django_app_siteuser"
        verbose_name = _("第三方平台用户")
        verbose_name_plural = _("第三方平台用户")
