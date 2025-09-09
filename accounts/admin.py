from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Order, Commission, MarketingMaterial,
    Product, AffiliateLink, CashoutRequest, Referral
)

# --------------------- ORDER ---------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "affiliate", "buyer_phone", "payment_method", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("affiliate__username", "buyer_phone", "product__name")
    actions = ["approve_orders", "reject_orders"]

    # Bulk approval (action)
    def approve_orders(self, request, queryset):
        created_count = 0
        for order in queryset:
            if order.status == "pending":
                order.status = "approved"
                order.save()
                if self._approve_order(order):
                    created_count += 1
        self.message_user(request, f"✅ {created_count} commissions created.")
    approve_orders.short_description = "Approve selected orders & credit commission"

    def reject_orders(self, request, queryset):
        updated = queryset.filter(status="pending").update(status="rejected")
        self.message_user(request, f"❌ {updated} orders rejected.")
    reject_orders.short_description = "Reject selected orders"

    # Single order approval (form save)
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status == "approved":
            self._approve_order(obj)

    # Shared commission creation logic
    def _approve_order(self, order):
        # Prevent duplicate commissions
        if not Commission.objects.filter(
            user=order.affiliate,
            sale_reference=f"Order {order.id} - {order.product.name}"
        ).exists():
            Commission.objects.create(
                user=order.affiliate,
                amount=order.product.commission_amount,
                commission_type="flat",
                status="pending",
                sale_reference=f"Order {order.id} - {order.product.name}"
            )
            # Update affiliate commission balance
            order.affiliate.commission_balance += order.product.commission_amount
            order.affiliate.save()
            return True
        return False


# --------------------- REFERRAL ---------------------
@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('user', 'referred_user', 'created_at')
    search_fields = ('user__username', 'referred_user__username')


# --------------------- CASHOUT REQUEST ---------------------
@admin.register(CashoutRequest)
class CashoutRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_amount', 'processing_fee', 'net_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username',)


# --------------------- PRODUCT ---------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'commission_amount')
    search_fields = ('name',)


# --------------------- AFFILIATE LINK ---------------------
@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'link')
    search_fields = ('user__username', 'product__name')


# --------------------- COMMISSION ---------------------
@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'commission_type', 'status', 'sale_reference', 'created_at')
    list_filter = ('commission_type', 'status')
    search_fields = ('user__username', 'sale_reference')


# --------------------- CUSTOM USER ---------------------
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'profile_picture')}),
        ('Bank Details', {'fields': ('bank_name', 'bank_account', 'beneficiary_name')}),
        ('Affiliate', {'fields': ('commission_balance', 'referral_code', 'referred_by')}),
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


# --------------------- MARKETING MATERIAL ---------------------
@admin.register(MarketingMaterial)
class MarketingMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "material_type", "uploaded_at")
    list_filter = ("material_type", "uploaded_at")
    search_fields = ("title",)
