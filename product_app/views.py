from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .models import Product, Attribute, AttributeValue, ProductVariant, ProductVariantAttribute
from .serializers import  ProductSerializer, AttributeSerializer, AttributeValueSerializer, ProductVariantSerializer, ProductVariantAttributeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from authentication_app.models import Vendor
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import render
# Product API

class ProductAPIView(APIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the user is a vendor or admin
        if not (hasattr(request.user, 'vendor_profile')):
            return Response({"detail": "Only vendors or admins can access this."}, status=status.HTTP_403_FORBIDDEN)

        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Check if the user is authenticated and is a vendor or admin
        if not request.user.is_authenticated or not (hasattr(request.user, 'vendor_profile')):
            return Response(
                {"detail": "Only vendors or admins can create product variants."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create the product with the vendor's ID
        data = request.data
        vendor = request.user.vendor_profile if hasattr(request.user, 'vendor_profile') else None
        data['created_by'] = vendor.id if vendor else None
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Attribute API  
class AttributeAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        attribute = Attribute.objects.all()
        serializer = AttributeSerializer(attribute, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if request.user.is_authenticated and (hasattr(request.user, 'vendor_profile')):
            data = request.data
            data['created_by'] = request.user.vendor_profile.id
            serializer = AttributeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Only vendors or admins can create product variant attributes."},
            status=status.HTTP_403_FORBIDDEN
        )

# Attribute Value API  
class AttributeValueAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        attributevalue = AttributeValue.objects.all()
        serializer = AttributeValueSerializer(attributevalue, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if request.user.is_authenticated and (hasattr(request.user, 'vendor_profile') or request.user.is_staff):
            data = request.data
            data['created_by'] = request.user.vendor_profile.id
            serializer = AttributeValueSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Only vendors or admins can create product variant attributes."},
            status=status.HTTP_403_FORBIDDEN
        )

# Product Variant API
class ProductVariantAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        product_variants = ProductVariant.objects.all() 
        serializer = ProductVariantSerializer(product_variants, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_authenticated and (hasattr(request.user, 'vendor_profile') or request.user.is_staff):
            data = request.data
            data['created_by'] = request.user.vendor_profile.id
            serializer = ProductVariantSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Only vendors or admins can create product variant attributes."},
            status=status.HTTP_403_FORBIDDEN
        )
        
# Product Variant Attribute API
class ProductVariantAttributeCreateAPIView(generics.CreateAPIView):
    queryset = ProductVariantAttribute.objects.all()
    serializer_class = ProductVariantAttributeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        vendor = getattr(user, 'vendor_profile', None)
        if not user.is_authenticated or (not vendor and not user.is_staff):
            raise PermissionDenied({"detail": "Only vendors or admins can create."})
        serializer.save(created_by=vendor if vendor else None)

# Product Variant Attribute API
class ProductVariantAttributeAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductVariantAttribute.objects.all()
    serializer_class = ProductVariantAttributeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['variant__product', 'attribute', 'value']  # Fields to filter by
    search_fields = ['variant__product__name', 'attribute__name', 'value__value']  # Fields to search by

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if hasattr(self.request.user, 'vendor_profile'):
                # Vendor: Only show their product variant attributes
                return ProductVariantAttribute.objects.filter(
                    variant__product__created_by=self.request.user.vendor_profile
                )
            else:
                # Authenticated customers or admins: Show all
                return ProductVariantAttribute.objects.all()
        else:
            # Guest users: Show all
            return ProductVariantAttribute.objects.all()
        
    def perform_update(self, serializer):
        if self.request.user.is_authenticated and (hasattr(self.request.user, 'vendor_profile') or self.request.user.is_staff):
            return super().perform_update(serializer)
        return Response(
            {"detail": "Only vendors or admins can update product variant attributes."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    def perform_destroy(self, instance):
        if self.request.user.is_authenticated and (hasattr(self.request.user, 'vendor_profile') or self.request.user.is_staff):
            return super().perform_destroy(instance)
        return Response(
            {"detail": "Only vendors or admins can delete product variant attributes."},
            status=status.HTTP_403_FORBIDDEN
        )
        
def product_variants_list(request):
    # Fetch all product variants
    product_variants = ProductVariant.objects.all()

    # Create a dictionary to store attributes for each product variant
    product_variant_data = []

    for variant in product_variants:
        attributes = ProductVariantAttribute.objects.filter(variant=variant)
        product_variant_data.append({
            "variant": variant,
            "attributes": attributes
        })

    context = {
        "product_variants": product_variant_data
    }
    return render(request, "product_variants_list.html", context)