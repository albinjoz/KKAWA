
from django.db import models

# Create your models here.


class RestaurantApproval(models.Model):

    store_id = models.CharField(max_length=150,unique=True)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images')
    address = models.TextField(max_length=200)
    pincode = models.CharField(max_length=10)
    certificate_or_license = models.CharField(max_length=50)
    store_charge = models.CharField(max_length=50)
    store_manager_name = models.CharField(max_length=50)
    store_manager_email = models.CharField(max_length=50)
    store_manager_phone = models.CharField(max_length=50)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class DeliveryPartnerApproval(models.Model):

    # partner_id = models.CharField(max_length=150,unique=True)
    # name = models.CharField(max_length=50)
    # photo = models.ImageField(upload_to='images')
    # address = models.TextField(max_length=200)
    # pincode = models.CharField(max_length=10)
    # license_number = models.CharField(max_length=50)
    # vehicle_number = models.CharField(max_length=50)
    # phone = models.CharField(max_length=15)
    # approved = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.name
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
    dlexpiry = models.DateField()
    dlUploadFront = models.ImageField(upload_to='images')
    dlUploadBack = models.ImageField(upload_to='images')

   
    # Vehicle number    

    vehicleNumber = models.CharField(max_length=15)
    vehicleMake = models.CharField(max_length=10)
    insuranceNumber = models.CharField(max_length=20)
    rcBookUpload = models.ImageField(upload_to='images')
    approved = models.BooleanField(default=False)
