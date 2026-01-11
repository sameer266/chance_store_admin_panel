# CORRECTED models.py with all critical fixes

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

from decimal import Decimal
from ckeditor.fields import RichTextField    
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver


class OTPVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True)
    otp_code = models.CharField(max_length=6,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.user.email}"
    
# -------------------------
# User Role Management
# -------------------------
class UserRole(models.Model):
    """Define user roles in the system"""
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role',null=True,blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_customer(self):
        return self.role == 'customer'
    
    def is_admin(self):
        return self.role == 'admin'


# -------------------------
# User Management
# -------------------------
class UserProfile(models.Model):
    GENDER_CHOICES=( ('male','Male'),
                    ('female','Female'))
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="profile")
    phone = models.CharField(max_length=15,null=True,blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    gender=models.CharField(max_length=10, choices=GENDER_CHOICES,null=True,blank=True)
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    PROVINCE_CHOICES = [
        ('province1', 'Koshi Province'),
        ('madhesh', 'Madhesh Province'),
        ('bagmati', 'Bagmati Province'),
        ('gandaki', 'Gandaki Province'),
        ('lumbini', 'Lumbini Province'),
        ('karnali', 'Karnali Province'),
        ('sudurpashchim', 'Sudurpashchim Province'),
    ]
    province = models.CharField(max_length=20, choices=PROVINCE_CHOICES, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_role(self):
        """Get user role"""
        try:
            return self.user.role.get_role_display()
        except:
            return 'No Role Assigned'


# -------------------------
# Category Management (Hierarchical)
# -------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    is_active = models.BooleanField(default=True)
    is_featured=models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['is_active', 'order']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


# -------------------------
# Product Management
# -------------------------
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    
    # Basic Info
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = RichTextField() 
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='For tracking')
    cut_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Stock Management
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True, help_text='Stock Keeping Unit')
    stock = models.PositiveIntegerField(default=0)
    low_stock_alert = models.PositiveIntegerField(default=5, help_text='Alert when stock reaches this level')
    
    # Product Details
    brand = models.CharField(max_length=100, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Weight in kg')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Shipping cost per unit for this product')
    estimated_days = models.CharField(max_length=50, blank=True, null=True, help_text='Estimated delivery time (days or string like "2-4 days")')
    
    # Images
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Status & Stats
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['slug']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if blank
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        import uuid
        if not self.sku:
            self.sku = uuid.uuid4().hex[:8].upper()
            
        super().save(*args, **kwargs)
    
    def in_stock(self):
        return self.stock > 0
    
    def is_low_stock(self):
        return 0 < self.stock <= self.low_stock_alert
    
    def discount_percentage(self):
        if self.cut_price and self.cut_price > self.price:
            return int(((self.cut_price - self.price) / self.cut_price) * 100)
        return 0

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0
    
    def __str__(self):
        return self.name


# -------------------------
# Cart & Wishlist
# -------------------------
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, help_text="For non-authenticated users")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        price = self.product.price
        return price * self.quantity

    def get_item_price(self):
        price = self.product.price
        return price
    
    def __str__(self):
        if self.user:
            return f"{self.user.username}'s cart - {self.product.name}"
        return f"Guest cart ({self.session_key}) - {self.product.name}"


# -------------------------
# Order Management
# -------------------------
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('esewa', 'eSewa'),
        ('khalti', 'Khalti'),
        ('imepay', 'IME Pay'),
        ('connectips', 'ConnectIPS'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # Order Info
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Shipping Info
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=20, null=True, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Order Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="cod")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Coupon
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Order Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
    
    # ✅ FIX #1: ADD MISSING calculate_totals() METHOD
    def calculate_totals(self):
        """
        Calculate order totals from order items.
        Called by signal when OrderItems are created/updated.
        """
        # Calculate subtotal from all order items
        self.subtotal = sum(item.get_total() for item in self.items.all()) or Decimal('0.00')
        
        # Calculate total shipping cost (sum of all item shipping costs × quantities)
        self.shipping_cost = sum(
            (item.shipping_cost or Decimal('0')) * item.quantity 
            for item in self.items.all()
        ) or Decimal('0.00')
        
        # Tax is already set (usually a percentage), so we use existing value
        # If you want to recalculate tax, you can do:
        # tax_rate = self.tax / Decimal('100') if self.tax else Decimal('0')
        # self.tax = self.subtotal * tax_rate
        
        # Calculate total: subtotal + shipping + tax - discount
        self.total = self.subtotal + self.shipping_cost + self.tax - self.discount
        
        # Save only specific fields to avoid triggering unnecessary signals
        self.save(update_fields=['subtotal', 'shipping_cost', 'total'])
    
    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_days = models.CharField(max_length=50, blank=True, null=True)
    
    def get_total(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        """
        Snapshot per-product shipping_cost and estimated_days at order time.
        """
        if self.product:
            try:
                if (self.shipping_cost is None or self.shipping_cost == 0) and hasattr(self.product, 'shipping_cost'):
                    self.shipping_cost = self.product.shipping_cost or 0
                if (not self.estimated_days) and hasattr(self.product, 'estimated_days'):
                    self.estimated_days = self.product.estimated_days
            except Exception:
                pass
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Unknown Product'}"


# -------------------------
# Reviews & Ratings
# -------------------------
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('product', 'user')
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"


# -------------------------
# Coupons & Discounts
# -------------------------
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    
    DISCOUNT_TYPES = [
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Minimum order value')
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Max discount amount (for percentage)')
    
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text='Total usage limit')
    usage_limit_per_user = models.PositiveIntegerField(null=True, blank=True, help_text='Per user limit')
    used_count = models.PositiveIntegerField(default=0)
    
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    categories = models.ManyToManyField('Category', blank=True, help_text='Applicable categories')
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self, user=None, cart_items=None):
        """Check if coupon is valid for the user and cart"""
        now = timezone.now()
        if not (self.is_active and self.valid_from <= now <= self.valid_to):
            return False, "This coupon is not active or has expired."

        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False, "This coupon has reached its usage limit."

        if user and self.usage_limit_per_user is not None:
            user_used_count = CouponUsage.objects.filter(user=user, coupon=self).count()
            if user_used_count >= self.usage_limit_per_user:
                return False, "You have already used this coupon the maximum number of times."

        if cart_items is not None:
            subtotal = sum(item.get_item_price() * item.quantity for item in cart_items)
            if subtotal < self.min_purchase:
                return False, f"Minimum order amount of Rs {self.min_purchase} required."

        return True, "Coupon is valid."

    def get_discount_amount(self, subtotal):
        """Calculate discount based on subtotal"""
        if self.discount_type == 'percent':
            discount = (self.discount_value / 100) * subtotal
            if self.max_discount is not None:
                discount = min(discount, self.max_discount)
        else:
            discount = self.discount_value
        return discount
    
    def __str__(self):
        return self.code


class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.first_name} used {self.coupon.code}"


# -------------------------
# Tax Configuration
# -------------------------
class TaxCost(models.Model):
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Tax percentage (e.g. 13 for 13%)")

    class Meta:
        verbose_name = 'Tax Setting'
        verbose_name_plural = 'Tax Settings'

    def __str__(self):
        return f"Tax: {self.tax}%"


# -------------------------
# Invoice
# -------------------------
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, null=True, unique=True, editable=False)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='invoices')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    payment_status = models.CharField(max_length=20, choices=[
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('failed', 'Failed')
    ], default='pending')
    
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.order.order_number}"


# -------------------------
# Organization Info
# -------------------------
class Organization(models.Model):
    name = models.CharField(max_length=200, default="My Store")
    logo = models.ImageField(upload_to='org/', blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    phone_secondary = models.CharField(max_length=15, blank=True)
    address = models.TextField()
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Organization Info'
        verbose_name_plural = 'Organization Info'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.pk and Organization.objects.exists():
            raise ValueError('Only one Organization instance allowed')
        super().save(*args, **kwargs)



# -------------------------
# Notifications
# -------------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    NOTIFICATION_TYPES = [
        ('order', 'Order Update'),
        ('product', 'Product Update'),
        ('message', 'Message'),
        ('promotion', 'Promotion'),
        ('other', 'Other'),
    ]
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


# -------------------------
# Slider & Banner
# -------------------------
class Slider(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='sliders/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title or f"Slider {self.id}"


class Banner(models.Model):
    PAGE_CHOICES = [
        ('home', 'Home Page'),
        ('products', 'Products Page'),
    ]

    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(max_length=500, blank=True, null=True)
    page = models.CharField(max_length=50, choices=PAGE_CHOICES, default='home', unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title or f"Banner {self.id}"


# -------------------------
# Supplier Management
# -------------------------
class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True, help_text='Additional notes about the supplier')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


# -------------------------
# Purchase History
# -------------------------
class Purchase(models.Model):
    """
    Purchase Order from supplier.
    This is the operational record that can be modified.
    """
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='purchases')
    purchase_date = models.DateField(default=timezone.now)
    bill_number = models.CharField(max_length=50, blank=True, null=True, help_text='Bill number from supplier')
    supplier_invoice_number = models.CharField(max_length=100, blank=True, help_text='Auto-generated full invoice number')
    purchase_order_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchase_date', '-created_at']
        indexes = [
            models.Index(fields=['-purchase_date']),
            models.Index(fields=['supplier', '-purchase_date']),
        ]

    def save(self, *args, **kwargs):
        """Generate full supplier invoice number"""
        if self.supplier and self.bill_number:
            today = timezone.now().strftime('%Y%m%d')
            supplier_code = ''.join(filter(str.isalpha, self.supplier.name[:3])).upper()
            if not supplier_code:
                supplier_code = 'SUP'
            clean_bill_number = str(self.bill_number).strip()
            self.supplier_invoice_number = f"{supplier_code}-{today}-{clean_bill_number}"
        elif not self.supplier_invoice_number:
            today = timezone.now().strftime('%Y%m%d')
            last_purchase = Purchase.objects.order_by('-id').first()
            next_id = (last_purchase.id + 1) if last_purchase else 1
            self.supplier_invoice_number = f"SUP-INV-{today}-{next_id:04d}"
            
        super().save(*args, **kwargs)
        
    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())
    
    def calculate_totals(self):
        """Calculate and update subtotal and total_amount based on items"""
        self.subtotal = sum(item.get_total() for item in self.items.all()) or Decimal('0.00')
        tax = Decimal(str(self.tax_amount or 0))
        discount = Decimal(str(self.discount or 0))
        self.total_amount = self.subtotal + tax - discount
        self.save(update_fields=['subtotal', 'total_amount'])
    
    def __str__(self):
        return f"Purchase {self.supplier_invoice_number} from {self.supplier.name if self.supplier else 'Unknown'}"


class PurchaseItem(models.Model):
    """Individual product items in a purchase order"""
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_items')
    product_name = models.CharField(max_length=255, help_text='Product name at time of purchase')
    product_sku = models.CharField(max_length=100, blank=True, null=True, help_text='Product SKU at time of purchase')
    product_image = models.ImageField(upload_to='purchases/products/', blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price per unit paid to supplier')
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
    
    def get_total(self):
        return self.purchase_price * self.quantity
    
    def save(self, *args, **kwargs):
        if self.product:
            if not self.product_name:
                self.product_name = self.product.name
            if not self.product_sku:
                self.product_sku = self.product.sku or ''
        
        super().save(*args, **kwargs)
        
        if self.purchase and self.purchase.pk:
            try:
                self.purchase.refresh_from_db()
                self.purchase.calculate_totals()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error calculating purchase totals: {e}")
    
    def delete(self, *args, **kwargs):
        purchase = self.purchase
        super().delete(*args, **kwargs)
        if purchase:
            purchase.calculate_totals()
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity} - Rs. {self.get_total()}"


# -------------------------
# Purchase Invoice (Historical Snapshot)
# -------------------------
class PurchaseInvoice(models.Model):
    """
    Historical invoice for purchases from suppliers.
    This is a SNAPSHOT that should NOT be modified after creation.
    """
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, related_name='invoice')
    
    # Supplier snapshot
    supplier_name = models.CharField(max_length=200, help_text='Supplier name at time of purchase')
    supplier_email = models.EmailField(blank=True)
    supplier_phone = models.CharField(max_length=15, blank=True)
    supplier_address = models.TextField(blank=True)
    supplier_city = models.CharField(max_length=100, blank=True)
    
    # Purchase details snapshot
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Invoice details
    purchase_date = models.DateField()
    supplier_invoice_number = models.CharField(max_length=100, blank=True)
    purchase_order_number = models.CharField(max_length=100, blank=True)
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('overdue', 'Overdue'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-purchase_date', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"PINV{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
    
    @property
    def outstanding_amount(self):
        try:
            return (self.total_amount - (self.paid_amount or Decimal('0.00')))
        except Exception:
            return self.total_amount
    
    def __str__(self):
        return f"Purchase Invoice {self.invoice_number} - {self.supplier_name}"


class PurchaseInvoiceItem(models.Model):
    """Individual items in purchase invoice - historical snapshot"""
    invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=100, blank=True, null=True)
    product_image = models.ImageField(upload_to='purchase_invoice_items/', blank=True, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"


# ===========================
# Services & Sales
# ===========================
class Service(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def discount_percentage(self):
        try:
            if not self.cost_price or not self.price:
                return None
            if self.cost_price <= 0:
                return None
            pct = (Decimal(self.cost_price) - Decimal(self.price)) / Decimal(self.cost_price) * Decimal('100')
            return pct.quantize(Decimal('0.01'))
        except Exception:
            return None


class ServiceBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_bookings')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='bookings')
    booking_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service} - {self.customer.username} on {self.booking_date}"


class SaleCustomer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def total_sales_amount(self):
        return self.sales.aggregate(total=models.Sum('total_amount'))['total'] or Decimal('0.00')
    
    def total_paid_amount(self):
        return self.sales.aggregate(total=models.Sum('paid_amount'))['total'] or Decimal('0.00')

    def total_outstanding_amount(self):
        return self.sales.aggregate(total=models.Sum('outstanding_amount'))['total'] or Decimal('0.00')

    def sales_count(self):
        return self.sales.count()
    
    def payment_status(self):
        if self.total_outstanding_amount() == 0 and self.total_sales_amount() > 0:
            return 'paid'
        elif self.total_outstanding_amount() > 0 and self.total_paid_amount() > 0:
            return 'partially_paid'
        elif self.total_outstanding_amount() > 0:
            return 'unpaid'
        return 'unpaid'


class Sale(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('unpaid', 'Unpaid'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit', 'Credit'),
    ]
    
    customer = models.ForeignKey(SaleCustomer, on_delete=models.CASCADE, related_name='sales')
    invoice_number = models.CharField(max_length=50, unique=True)
    sale_date = models.DateTimeField(auto_now_add=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_notes = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Sale #{self.invoice_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.invoice_number = f"SALE-{timestamp}"
        
        self.outstanding_amount = self.total_amount - self.paid_amount
        
        if self.outstanding_amount <= 0:
            self.payment_status = 'paid'
        elif self.paid_amount > 0:
            self.payment_status = 'partially_paid'
        else:
            self.payment_status = 'unpaid'
        
        super().save(*args, **kwargs)


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class SalePayment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=Sale.PAYMENT_METHOD_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment of Rs.{self.amount} for Sale #{self.sale.invoice_number}"


# ===========================
# SIGNALS
# ===========================
@receiver(post_save, sender=Order)
def handle_order_payment_status_change(sender, instance, created, **kwargs):
    """Auto-update order status to 'delivered' when payment is marked as 'paid'"""
    if created:
        return
    
    if instance.payment_status == 'paid':
        if instance.status not in ['cancelled', 'refunded', 'delivered']:
            Order.objects.filter(pk=instance.pk).update(
                status='delivered',
                delivered_at=timezone.now() if not instance.delivered_at else instance.delivered_at
            )
    
    # Sync invoice payment status
    try:
        if instance.user:
            invoice = Invoice.objects.filter(order=instance, customer=instance.user).first()
            if invoice:
                invoice_status_map = {
                    "unpaid": "pending",
                    "paid": "paid",
                    "failed": "failed",
                    "refunded": "failed"
                }
                new_invoice_status = invoice_status_map.get(instance.payment_status, invoice.payment_status)
                if invoice.payment_status != new_invoice_status:
                    invoice.payment_status = new_invoice_status
                    invoice.save(update_fields=['payment_status'])
    except Exception:
        pass


@receiver(post_save, sender=OrderItem)
def update_order_totals_on_item_change(sender, instance, created, **kwargs):
    """Recalculate Order totals whenever an OrderItem is created/updated"""
    try:
        if instance.order_id:
            instance.order.calculate_totals()
    except Exception:
        pass


@receiver(post_delete, sender=OrderItem)
def update_order_totals_on_item_delete(sender, instance, **kwargs):
    """Recalculate Order totals when an OrderItem is deleted"""
    try:
        if instance.order_id:
            order = Order.objects.filter(pk=instance.order_id).first()
            if order:
                order.calculate_totals()
    except Exception:
        pass


@receiver(post_save, sender=Order)
def ensure_order_items_snapshots(sender, instance, created, **kwargs):
    """Ensure order items have shipping snapshot filled"""
    try:
        for it in instance.items.all():
            if (not it.shipping_cost or it.shipping_cost == 0) or not it.estimated_days:
                it.save()
    except Exception:
        pass


# ✅ FIX #2: CORRECT UserRole SIGNAL
@receiver(post_save, sender=User)
def create_user_role_and_profile(sender, instance, created, **kwargs):
    """Automatically creates UserRole and UserProfile when a new user is created"""
    if created and instance.is_superuser:
        UserRole.objects.get_or_create(user=instance, defaults={'role': 'admin'})
        UserProfile.objects.get_or_create(user=instance)