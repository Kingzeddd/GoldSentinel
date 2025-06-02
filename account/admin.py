from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
# Corrected imports:
from .models.user_model import UserModel
from .models.authority_model import AuthorityModel
from .models.user_authority_model import UserAuthorityModel

# Inline for UserAuthorityModel
class UserAuthorityInline(admin.TabularInline):
    model = UserAuthorityModel
    extra = 1  # Number of empty forms to display
    fields = ('authority', 'is_primary', 'status', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    can_delete = True
    verbose_name = _("User Authority")
    verbose_name_plural = _("User Authorities")

# Custom UserModel Admin
class UserAdmin(BaseUserAdmin):
    inlines = [UserAuthorityInline]
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'get_authorities', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'user_authorities__authority__name')

    # Use default fieldsets and add custom ones
    # BaseUserAdmin.fieldsets structure:
    # (None, {"fields": ("username", "password")}),
    # (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
    # (
    #     _("Permissions"),
    #     {
    #         "fields": (
    #             "is_active",
    #             "is_staff",
    #             "is_superuser",
    #             "groups",
    #             "user_permissions",
    #         ),
    #     },
    # ),
    # (_("Important dates"), {"fields": ("last_login", "date_joined")}),

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'job_title', 'institution')}),
        (_('Regional Access'), {'fields': ('authorized_region',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    def get_authorities(self, obj):
        authorities = obj.user_authorities.filter(status='ACTIVE').select_related('authority')
        primary_authority = None
        other_authorities = []
        for ua in authorities:
            if ua.is_primary:
                primary_authority = ua.authority.name
            else:
                other_authorities.append(ua.authority.name)

        display_list = []
        if primary_authority:
            display_list.append(f"<strong>{primary_authority} (Primary)</strong>")
        display_list.extend(other_authorities)

        return ", ".join(display_list) if display_list else "N/A"

    get_authorities.short_description = _('Authorities')
    get_authorities.allow_tags = True # To render HTML if used, e.g. for bolding primary

# Custom AuthorityModel Admin (Optional, can be simple for now)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

# Register models
admin.site.register(UserModel, UserAdmin)
admin.site.register(AuthorityModel, AuthorityAdmin)
# UserAuthorityModel is managed via the inline, no need to register it separately.
