from django.db import models
import json
from pathlib import Path
import logging
from django.core.exceptions import ValidationError
from accounts_app.models import User
from django.db.models import Q


logger = logging.getLogger('watchers_app')

TOFA_PRODUCTS_PATH = Path("../config/Tofa_products_dictionary.json")

if TOFA_PRODUCTS_PATH.is_file():
    with open(TOFA_PRODUCTS_PATH, 'r', encoding='utf-8') as f:
        FULL_DICTIONARY = json.load(f)
else:
    logger.error(f"Configuration file does not exist: {TOFA_PRODUCTS_PATH}")
    raise RuntimeError("Configuration file does not exist.")

CATEGORY_CHOICES = [(k, v) for k, v in FULL_DICTIONARY['CATEGORY_CHOICES'].items()]
SUB_CATEGORY_CHOICES = [(k, v) for k, v in FULL_DICTIONARY['SUB_CATEGORY_CHOICES'].items()]


class Categorization(models.Model):
    main_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, db_index=True)
    sub_category = models.CharField(max_length=100, choices=SUB_CATEGORY_CHOICES, db_index=True)
    exposure = models.BooleanField()

    def __str__(self):
        return f"{self.main_category} - {self.sub_category}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['main_category', 'sub_category'], name='unique_main_sub')
        ]

class TofaProductsRepository(models.Model):
    item_name = models.CharField(max_length=100, primary_key=True)
    category = models.ForeignKey(Categorization, on_delete=models.SET('Deleted'),null=False)
    brand=models.CharField(max_length=100,null=False)
    price=models.FloatField(max_length=1000,null=False)
    item_description = models.CharField(max_length=1000,null=False)
    item_quantity = models.BigIntegerField(default=0)

    def __str__(self):
        return self.item_name

    def clean(self):
        if self.item_quantity < 0:
            raise ValidationError("Quantity cannot be negative.")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['item_name', 'category','brand'], name='product_uniqueness')
        ]

class TofaProductsOrderID(models.Model):
    order_creation_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET('Deleted'))

    def __str__(self):
        return f"{self.user}-{self.order_creation_time}"

class bill_id(models.Model):
    STATUS=[
        ('CUSTOMER_REQUEST_TO_CLOSE','CUSTOMER_REQUEST_TO_CLOSE'),
        ('SETTELLED','SETTELLED'),
        ('RETURNED_TO_CUSTOMER','RETURNED_TO_CUSTOMER')]
    bill_value=models.BigIntegerField(default=0)
    bill_user=models.ForeignKey(User,on_delete=models.SET('Deleted'))
    bill_issue_time=models.DateTimeField(auto_now_add=True)
    bill_status=models.CharField(choices=STATUS,default='CUSTOMER_REQUEST_TO_CLOSE')
    bill_closure_time=models.DateTimeField(null=True)

    def __str__(self):
        return f"bill Amount={self.bill_value} User={self.bill_user}"
    
class TofaProductsOrder(models.Model):
    ORDER_STATUS = [
        ('INCart_Pending', 'INCart_Pending'),
        ('INPreparation', 'INPreparation'),
        ('Served', 'Served'),
        ('PAID_Closed', 'PAID_Closed')
    ]
    item_name = models.ForeignKey(TofaProductsRepository, on_delete=models.SET('Deleted'))
    user = models.ForeignKey(User, on_delete=models.SET('Deleted'))
    status = models.CharField(max_length=20, choices=ORDER_STATUS, db_index=True,default='INCart_Pending')
    placed_in_cart_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    fullfilled_at = models.DateTimeField(blank=True, null=True)
    count=models.IntegerField()
    table_number=models.IntegerField(null=True,blank=True)
    order_number = models.ForeignKey(TofaProductsOrderID, on_delete=models.SET('Deleted'), null=True, blank=True)
    bill_number=models.ForeignKey(bill_id, on_delete=models.SET('Deleted'), null=True, blank=True)

    def __str__(self):
        return f"Order({self.status}) of {self.item_name.item_name} by {self.user}"

class Meta:
    constraints = [
        models.UniqueConstraint(fields=['item_name', 'user', 'status', 'order_number'],name='unique_item_incart'),
        models.CheckConstraint( check=Q(count__gt=0),name='count_must_be_positive'),
    ]

