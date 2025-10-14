from django.contrib import admin
from .models import (
    MAuthUser,
    MAuthUserCredential,
    MCaptcha,
    MEmailCaptcha,
    MEmailCredential,
    MSiteUser,
    MSMSCaptcha,
    MSMSCaptchaCredential,
)


@admin.register(MEmailCredential)
class AEmailCredential(admin.ModelAdmin):
    pass


@admin.register(MCaptcha)
class ACaptcha(admin.ModelAdmin):
    pass


@admin.register(MSMSCaptchaCredential)
class ASMSCaptchaCredential(admin.ModelAdmin):
    pass


@admin.register(MEmailCaptcha)
class AEmailCaptcha(admin.ModelAdmin):
    pass


@admin.register(MSMSCaptcha)
class ASMSCaptcha(admin.ModelAdmin):
    pass


@admin.register(MSiteUser)
class ASiteUser(admin.ModelAdmin):
    search_fields = ["id", "name", "email", "username", "identifier"]
    autocomplete_fields = ["region"]


@admin.register(MAuthUserCredential)
class AAuthUserCredential(admin.ModelAdmin):
    pass


@admin.register(MAuthUser)
class AuthUser(admin.ModelAdmin):
    pass
