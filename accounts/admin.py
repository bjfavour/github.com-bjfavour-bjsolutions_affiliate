from django.contrib import admin
from .models import Order
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import Commission,  MarketingMaterial, Product, AffiliateLink, CashoutRequest, Referral


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "affiliate", "buyer_name", "payment_method", "status")
    actions = ["mark_as_paid"]

    def mark_as_paid(self, request, queryset):
        for order in queryset:
            if order.status != "paid":
                order.status = "paid"
                order.save()

                # Assign commission
                Commission.objects.create(
                    user=order.affiliate,
                    amount=order.product.commission_amount,
                    description=f"Commission for Order {order.id} - {order.product.name}",
                )
        self.message_user(request, "Selected orders marked as Paid and commissions assigned.")
    mark_as_paid.short_description = "Mark selected orders as Paid & Assign Commission"


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('user', 'referred_user', 'created_at')
    search_fields = ('user__username', 'referred_user__username')

@admin.register(CashoutRequest)
class CashoutRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_amount', 'processing_fee', 'net_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'commission_amount')
    search_fields = ('name',)


@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'link')
    search_fields = ('user__username', 'product__name')

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'commission_type', 'status', 'sale_reference', 'created_at')
    list_filter = ('commission_type', 'status')
    search_fields = ('user__username', 'sale_reference')


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'profile_picture')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(MarketingMaterial)
class MarketingMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "material_type", "uploaded_at")
    list_filter = ("material_type", "uploaded_at")
    search_fields = ("title",)


