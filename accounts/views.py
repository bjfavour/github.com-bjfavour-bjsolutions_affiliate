from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum
from decimal import Decimal

from .serializers import (
    RegisterSerializer, ProfileSerializer, DashboardSerializer,
    LoginSerializer, CashoutRequestSerializer,
    MarketingMaterialSerializer, ProductSerializer,
    AffiliateLinkSerializer, OrderSerializer
)
from .models import (
    CustomUser, Withdrawal, Commission, CashoutRequest,
    MarketingMaterial, Product, AffiliateLink, Order
)
from rest_framework.permissions import IsAuthenticated


# --------------------- DASHBOARD ---------------------
from collections import defaultdict
from decimal import Decimal
from django.db.models import Sum

class DashboardView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # 1) High-level counters
        total_earnings = user.balance
        total_referrals = user.referral_made.count()

        pending_withdrawals = Withdrawal.objects.filter(
            user=user, status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # ✔ Show the *available* commission (what the user can withdraw now)
        available_commission = user.commission_balance

        # 2) Total approved cashout (for your "Total Cashed Out" figure)
        total_cashout = CashoutRequest.objects.filter(
            user=user, status='approved'
        ).aggregate(total=Sum('net_amount'))['total'] or 0

        # 3) Build a running-balance history for the chart
        #    + Commission rows add to balance
        #    + Cashout requests subtract from balance
        # NOTE: Your current CreateView *already deducts at request time*,
        # so we subtract on created_at for BOTH pending & approved requests.
        # If you later switch to "deduct on approval only", change the date
        # below to use `updated_at` for approved requests.
        events_by_date = defaultdict(Decimal)

        # + commissions
        for c in Commission.objects.filter(user=user).only("amount", "created_at"):
            events_by_date[c.created_at.date()] += Decimal(c.amount)

        # - cashouts (subtract requested_amount)
        for co in CashoutRequest.objects.filter(user=user).exclude(status='rejected').only(
            "requested_amount", "status", "created_at", "updated_at"
        ):
            # current behavior (deduct on request):
            date_for_event = co.created_at.date()

            # If you later deduct on approval only, use:
            # date_for_event = (co.updated_at.date() if co.status == "approved" else None)
            # if date_for_event is None: continue

            events_by_date[date_for_event] -= Decimal(co.requested_amount)

        # turn events into a sorted running balance
        history = []
        running = Decimal("0.00")
        for d in sorted(events_by_date.keys()):
            running += events_by_date[d]
            history.append({
                "date": d.isoformat(),
                "amount": float(running)  # chart expects simple numbers
            })

        # 4) Optional: keep your old pending_commissions if something in FE reads it
        pending_commissions = Commission.objects.filter(
            user=user, status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # 5) Cashout history for the table
        cashouts = CashoutRequest.objects.filter(user=user).order_by("-created_at")
        cashout_history = [
            {
                "date": c.created_at.strftime("%Y-%m-%d"),
                "requested": float(c.requested_amount),
                "net": float(c.net_amount),
                "status": c.status,
            }
            for c in cashouts
        ]

        return Response({
            "total_earnings": total_earnings,
            "total_referrals": total_referrals,
            "pending_withdrawals": pending_withdrawals,
            "pending_commissions": pending_commissions,   # keep for backward-compat
            "available_commission": float(available_commission),  # ✅ new: what matters
            "total_cashout": float(total_cashout),
            "commission_history": history,                # ✅ now a running balance
            "cashout_history": cashout_history,           # ✅ to fill your table
        })



# --------------------- PRODUCTS & ORDERS ---------------------
class PlaceOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(affiliate=self.request.user)


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class GetAffiliateLinkView(generics.RetrieveAPIView):
    serializer_class = AffiliateLinkSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "product_id"

    def get_object(self):
        product_id = self.kwargs.get("product_id")
        product = Product.objects.get(id=product_id)
        link, created = AffiliateLink.objects.get_or_create(
            user=self.request.user, product=product
        )
        return link


# --------------------- MARKETING MATERIALS ---------------------
class MarketingMaterialsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        materials = MarketingMaterial.objects.all().order_by("-uploaded_at")
        serializer = MarketingMaterialSerializer(materials, many=True)

        grouped = {"image": [], "video": [], "pdf": []}
        for item in serializer.data:
            grouped[item["material_type"]].append(item)

        return Response(grouped)


# --------------------- CASHOUT ---------------------
MINIMUM_CASHOUT_THRESHOLD = Decimal('5000.00')
PROCESSING_FEE = Decimal('1000.00')


class CashoutRequestCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CashoutRequestSerializer

    def create(self, request, *args, **kwargs):
        user = request.user

        # ✅ NEW: handle action=history
        action = request.data.get("action")
        if action == "history":
            cashout_history = CashoutRequest.objects.filter(user=user).order_by('-created_at')
            serializer = CashoutRequestSerializer(cashout_history, many=True)

            total_cashout = CashoutRequest.objects.filter(
                user=user, status='approved'
            ).aggregate(total=Sum('net_amount'))['total'] or 0

            return Response({
                "commission_balance": user.commission_balance,
                "total_cashout": float(total_cashout),
                "cashout_history": serializer.data,
            })

        # ✅ Normal POST (requesting a new cashout)
        requested_amount = Decimal(request.data.get('requested_amount', '0'))

        if user.commission_balance < MINIMUM_CASHOUT_THRESHOLD:
            return Response({"detail": "Insufficient commission balance for cashout."},
                            status=status.HTTP_400_BAD_REQUEST)

        if requested_amount > user.commission_balance:
            return Response({"detail": "Requested amount exceeds commission balance."},
                            status=status.HTTP_400_BAD_REQUEST)

        if requested_amount <= PROCESSING_FEE:
            return Response({"detail": "Requested amount must be greater than processing fee."},
                            status=status.HTTP_400_BAD_REQUEST)

        net_amount = requested_amount - PROCESSING_FEE

        cashout_request = CashoutRequest.objects.create(
            user=user,
            requested_amount=requested_amount,
            processing_fee=PROCESSING_FEE,
            net_amount=net_amount,
            status='pending',
        )

        # Deduct requested amount immediately
        user.commission_balance -= requested_amount
        user.save()

        # Return updated balance + history
        cashout_history = CashoutRequest.objects.filter(user=user).order_by('-created_at')
        serializer = CashoutRequestSerializer(cashout_history, many=True)

        total_cashout = CashoutRequest.objects.filter(
            user=user, status='approved'
        ).aggregate(total=Sum('net_amount'))['total'] or 0

        return Response({
            "commission_balance": user.commission_balance,
            "total_cashout": float(total_cashout),
            "cashout_history": serializer.data,
        }, status=status.HTTP_201_CREATED)



# --------------------- PROFILE ---------------------
class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


# --------------------- AUTH ---------------------
@api_view(["POST"])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Registration successful. Wait for admin approval."},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
