
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser

from accounts.managers import CustomUserManager
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=10, unique=True, blank=True, null=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(_('email address'))
    phone = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True, blank=True, null=True)
    token = models.CharField(max_length=100)

    status = models.BooleanField(default=True)
    created_at = models.DateField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    objects = CustomUserManager()

#****************************************************************************************************************


class verify(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,13}$', message="Phone number must be entered in the format: '+999999999'. Up to 13 digits allowed.")
    phone = models.CharField(max_length=13, blank=True,)
    email = models.EmailField(blank=True)
    ph_otp = models.PositiveIntegerField()
    count = models.IntegerField(default=0, help_text='Number of otp sent')
    status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.phone) + ' is sent ' + str(self.ph_otp)


#********************************************************************************************************************


# class Token (models.Model):
#     # userId = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='token_userid')
#     userId = models.CharField(max_length=10, unique=True, blank=True, null=True)
#     token = models.CharField(max_length=10, unique=True, blank=True, null=True)
#     expireAt = models.DateTimeField(auto_now=True)

#*********************************************************************************


class Address(models.Model):
    userId = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=100,  blank=True, null=True)
    city = models.CharField(max_length=20,  blank=True, null=True)
    location = models.CharField(max_length=20,  blank=True, null=True)
    landmark = models.CharField(max_length=20,  blank=True, null=True)
    district = models.CharField(max_length=20,  blank=True, null=True)
    state = models.CharField(max_length=20,  blank=True, null=True)
    country = models.CharField(max_length=20,  blank=True, null=True)
    isDefault = models.BooleanField(default=False)

#********************************************************************************************************************

class Gallery(models.Model):
    name = models.CharField(max_length=150)
    url = models.CharField(max_length=150)

#********************************************************************************************************************

class Store(models.Model):
    storeType = models.CharField(max_length=150)
    store_id = models.CharField(max_length=150)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    gallery = models.ManyToManyField(Gallery)

    gstNumber = models.CharField(max_length=25)
    fssaiLicenseNumber = models.CharField(max_length=25)
    phone = models.CharField(max_length=50)
    address = models.TextField(max_length=200)
    pincode = models.CharField(max_length=10)
    
    landmark = models.CharField(max_length=50)
    latitude = models.DecimalField(blank=True, max_digits=9, decimal_places=6, default=None, null=True)
    longitude = models.DecimalField(blank=True, max_digits=9, decimal_places=6, default=None, null=True)
    certificate_or_license = models.CharField(max_length=50)     
    store_charge = models.CharField(max_length=50)

    choices = (
        ('pickup and drop', 'pickup and drop'),
        ('Takeaway', 'Takeaway'),
        ('', ''),
    )
    delivery_type = models.CharField(max_length=50, choices=choices, default="pickup and drop")
    delivery_radius = models.CharField(max_length=25)
    approx_delivery_time = models.CharField(max_length=25)
    time = models.DateTimeField(auto_now=True)
    
    store_manager_name = models.CharField(max_length=50)
    store_manager_email = models.CharField(max_length=50)
    store_manager_phone = models.CharField(max_length=50)
    
    bankName = models.CharField(max_length=50)
    accountName = models.CharField(max_length=20)
    accountNumber = models.CharField(max_length=25, unique= True)
    ifscCode = models.CharField(max_length=20)
    branchName = models.CharField(max_length=25)

    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name

#********************************************************************************************************************


class Restaurant_earning(models.Model):
    earnings = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(auto_now=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.store)+"'s earnings on " + str(self.date)+" is R.s " + str(self.earnings)


#********************************************************************************************************************


class Item_category(models.Model):
    item_category = models.CharField(max_length=50)

    def __str__(self):
        return self.item_category


class Item(models.Model):

    itemId = models.CharField(max_length=50)
    item_name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    price = models.DecimalField(blank=True, max_digits=9, decimal_places=3, default=0, null=True)
    itemStore = models.ForeignKey(Store, on_delete=models.CASCADE)
    ItemCategory = models.ForeignKey(Item_category, on_delete=models.CASCADE)
    image = models.ManyToManyField(Gallery)
    date = models.DateField(auto_now=True)
    discount = models.DecimalField(blank=True, max_digits=9, decimal_places=3, default=0, null=True)
    tax = models.DecimalField(blank=True, max_digits=9, decimal_places=3, default=0, null=True)
    

    def __str__(self):
        return self.item_name

#********************************************************************************************************************


class Cart(models.Model):
    
    user = models.CharField(max_length=25, unique=True, blank=True, null=True)
    item = models.ManyToManyField(Item, related_name='cart_items')
    quantity = models.IntegerField(default=0)   
    deliveryCharge = models.IntegerField(default=0)
    otherCharges = models.IntegerField(default=0)
    grandTotal = models.IntegerField(default=0)
    date= models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.quantity} numbers of  {self.item_name}"

    @property
    def get_total(self):
        total = self.item.price * self.quantity
        return total

#********************************************************************************************************************

class Wishlist(models.Model):
    user = models.CharField(max_length=25, unique=True, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

class Order(models.Model):

    method = (('cash', 'cash'), ('card', 'card'))
    pstatus = (('pending','pending'),('success','success'),('canceled','canceled'))

    dstatus = (('processing', 'processing'),
              ('processed_but_not_picked', 'processed_but_not_picked'),
              ('out_for_delivery', 'out_for_delivery'),
              ('delivered', 'delivered'),)

    user = models.CharField(max_length=25, unique=True, blank=True, null=True)
    items = models.ForeignKey(Item, on_delete=models.CASCADE)
    storeDetails = models.ForeignKey(Store, on_delete=models.CASCADE) 
    totalAmount =  models.IntegerField(default=0)
    
    couponEnabled = models.BooleanField(default=False)
    couponDetails = models.CharField(max_length=25, unique=True, blank=True, null=True)
    paymentMethods = models.CharField(max_length=25, choices=method)
    paymentStatus = models.CharField(max_length=25, choices=pstatus)
    
    deliveryStatus = models.CharField(max_length=25, choices=dstatus)
    confirmToken = models.BooleanField(default=False)

#********************************************************************************************************************


class Card(models.Model):
    user = models.CharField(max_length=25, unique=True, blank=True, null=True)
    cardNumber = models.CharField(max_length=16, unique=True, blank=True, null=True)
    cvv= models.CharField(max_length=25, unique=True, blank=True, null=True)
    validUpto = models.DateField(auto_now=True)
    date = models.DateTimeField(auto_now=True)
    isDefault = models.BooleanField(default=False)


# **************************************************************************************

class Invoice(models.Model):
    user = models.CharField(max_length=25, unique=True, blank=True, null=True)
    orderId = models.ForeignKey(Order, on_delete=models.CASCADE)
    url = models.CharField(max_length=250, blank=True, unique=True,null=True)
    date = models.DateTimeField(auto_now=True)

# **************************************************************************************

class Review(models.Model):
    user = models.CharField(max_length=25, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.CharField(max_length=100, blank=True, null=True)

# **************************************************************************************



class TicketGenerate(models.Model):
    userId = models.CharField(max_length=25, blank=True, null=True)
    # admimId = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    adminId = models.CharField(max_length=25, blank=True, null=True)
    meassage = models.TextField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=25, blank=True, null=True)
    attachment = models.FileField(upload_to='images')



class Chat(models.Model):
    ticket = models.ForeignKey(TicketGenerate,on_delete=models.CASCADE)
    # chat = models.ManyToManyField( related_name='Ticket_genrationCustomuser')
    reply = models.CharField(max_length=100, blank=True, null=True)
    # meassage = models.TextField(max_length=100, blank=True, null=True)

# **************************************************************************************


class DeliveryPartnerProfile(models.Model):


    TWO_WHEELER = "two wheeler"
    THREE_WHEELER = "three wheeler"
    FOUR_WHEELER = "four wheeler"

    TYPE = (
        (TWO_WHEELER, "two wheeler"),
        (THREE_WHEELER, "three wheeler"),
        (FOUR_WHEELER, "four wheeler"))


    userId = models.CharField(max_length=25, unique=True, blank=True, null=True)
    vehicleType= models.CharField(max_length= 25,choices=TYPE, blank=None, null=True)
    city  = models.CharField(max_length=20)
    locality = models.CharField(max_length=20)
    workingHours = models.TextField(max_length=100)

    panCardNumber = models.CharField(max_length=20)
    uploadPanCard = models.ImageField(upload_to='images')
    nameAsOnPandcard = models.CharField(max_length=20)

    # personaldetails
    aadarNumber = models.IntegerField()
    dateOfBirth = models.DateField()
    fatherName = models.CharField(max_length=10)
    address1 = models.CharField(max_length=10)
    address2 = models.CharField(max_length=10)
    district = models.CharField(max_length=10)
    state = models.CharField(max_length=10)
    pincode = models.CharField(max_length=10)


    # Driving Licence
    licenseNumber = models.CharField(max_length=10)
    dlexpiry = models.CharField(max_length=10)
    dlUploadFront = models.ImageField(upload_to='images')
    dlUploadBack = models.ImageField(upload_to='images')

   
    # Vehicle number    

    vehicleNumber = models.CharField(max_length=15)
    vehicleMake = models.CharField(max_length=10)
    insuranceNumber = models.CharField(max_length=20)
    rcBookUpload = models.ImageField(upload_to='images')
    approved = models.BooleanField(default=False)




class CustomerSupport(models.Model):

    SOLVED = "solved"
    NOTSOLVED = "notsolved"

    STATUS_ENABLED = (
        (SOLVED, "solved"),
        (NOTSOLVED, "notsolved")
    )

    EMAIL = "email"
    PHONE = "phone"

    TYPE = (
        (EMAIL, "email"),
        (PHONE, "phone")
    )

    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    token = models.CharField(max_length= 50, primary_key = True)
    complaint = models.CharField(max_length=100)
    status = models.CharField(max_length= 10,choices=STATUS_ENABLED, blank=None, null=True)
    contentType = models.CharField(max_length= 10,choices=TYPE, blank=None, null=True)
