from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, ProfileSerializer, DashboardSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from rest_framework import generics, permissions
from .models import CustomUser, Withdrawal, Commission, CashoutRequest
from django.db.models import Sum
from decimal import Decimal
from .serializers import CashoutRequestSerializer
from rest_framework.permissions import IsAuthenticated
from .models import MarketingMaterial
from .serializers import MarketingMaterialSerializer
from rest_framework import generics, permissions
from .models import Product, AffiliateLink, Order, Commission
from .serializers import ProductSerializer, AffiliateLinkSerializer, OrderSerializer

class PlaceOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Attach affiliate automatically
        serializer.save(affiliate=self.request.user)

# View all products
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

# Get or create affiliate link for a product
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

class MarketingMaterialsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        materials = MarketingMaterial.objects.all().order_by("-uploaded_at")
        serializer = MarketingMaterialSerializer(materials, many=True)

        # Group by type
        grouped = {"image": [], "video": [], "pdf": []}
        for item in serializer.data:
            grouped[item["material_type"]].append(item)

        return Response(grouped)

MINIMUM_CASHOUT_THRESHOLD = Decimal('5000.00')
PROCESSING_FEE = Decimal('1000.00')

class CashoutRequestCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CashoutRequestSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
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

        # Deduct requested amount from user's commission balance immediately
        user.commission_balance -= requested_amount
        user.save()

        # Return updated commission balance and cashout history
        cashout_history = CashoutRequest.objects.filter(user=user).order_by('-created_at')
        serializer = CashoutRequestSerializer(cashout_history, many=True)

        return Response({
            "commission_balance": user.commission_balance,
            "cashout_history": serializer.data,
        }, status=status.HTTP_201_CREATED)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

class DashboardView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DashboardSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        total_earnings = user.balance

        # Correct related_name for referrals made by the user
        total_referrals = user.referral_made.count()

        # Sum of pending withdrawals
        pending_withdrawals = Withdrawal.objects.filter(
            user=user,
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Sum of pending commissions
        pending_commissions = Commission.objects.filter(
            user=user,
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0

        data = {
            "total_earnings": total_earnings,
            "total_referrals": total_referrals,
            "pending_withdrawals": pending_withdrawals,
            "pending_commissions": pending_commissions,
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)

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
