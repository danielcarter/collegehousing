from django.db import models
from django.urls import reverse


class Stat(models.Model):
    name = models.CharField(max_length=255, null=True)
    value = models.DecimalField(decimal_places = 2, max_digits = 20, null=True)

    def __str__(self):
        return str(self.name)

class Owner(models.Model):
    name = models.CharField(max_length=255, null=True)
    address1 = models.CharField(max_length=255, null=True)
    address2 = models.CharField(max_length=255, null=True)
    address3 = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    zip = models.CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.name)

class RentObservation(models.Model):

    rent = models.IntegerField()
    sqft = models.IntegerField()
    bedrooms = models.IntegerField()
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.rent)

class ManagementObservation(models.Model):

    company = models.CharField(max_length=255, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.company + " // " + str(self.date))

class FireReport(models.Model):

    ems = models.BooleanField()
    date = models.DateTimeField()
    description = models.CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.date) + " // " + self.description

class PoliceReport(models.Model):

    date = models.DateTimeField(null=True)
    activity = models.CharField(max_length=255, null=True)
    disposition = models.CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.date) + " // " + str(self.activity)

    def year(self):
        return self.date.year

class Value(models.Model):

    value = models.IntegerField(default=0)
    year = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        return str(self.value) + " // " + str(self.year)

class Property(models.Model):

    address = models.CharField(max_length=255, default="")
    name = models.CharField(max_length=255, default="Unnamed Complex")
    year_built = models.IntegerField(blank=True, null=True, default=0)
    units = models.IntegerField(blank=True, null=True)
    beds = models.IntegerField(blank=True, null=True)
    section_8 = models.BooleanField(default = False)
    act_ally = models.BooleanField(default = False)
    lease_type = models.CharField(max_length=255, default="")
    rents = models.ManyToManyField(RentObservation)
    police_reports = models.ManyToManyField(PoliceReport)
    fire_reports = models.ManyToManyField(FireReport)
    management_companies = models.ManyToManyField(ManagementObservation)
    values = models.ManyToManyField(Value)
    owners = models.ManyToManyField(Owner, through="PropertyOwner")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, default=0)
    notes = models.TextField(null = True, blank = True)

    @property
    def simple_address(self):
        return(self.address.replace(", SAN MARCOS, TX 78666",""))

    @property
    def current_2bdrm_rent(self):
        tmp = self.rents.all().order_by('-date').filter(bedrooms__exact = 2).first()
        if tmp is not None:
            return(tmp.rent)
        else:
            return("unknown")

    @property
    def current_property_value(self):
        tmp = self.values.all().order_by('-year').first()
        if tmp is not None:
            return(tmp.value)
        else:
            return("unknown")

    @property
    def current_management(self):
        tmp = self.management_companies.all().order_by('-date').first()
        if tmp is not None:
            return(tmp.company)
        else:
            return("unknown")

    @property
    def current_owners(self):
        all_owners = PropertyOwner.objects.filter(property = self).order_by("-year")
        current_owners = ""
        latest_year = 0

        i = 0
        for owner in all_owners:
            if owner.year >= latest_year:
                latest_year = owner.year
                ## Used to link this ...
                current_owners = current_owners + "<a href='" + reverse('owner', args=[owner.owner.id]) + "' title='Ownership Information for " + owner.owner.name + "'>" + owner.owner.name + "</a>, "

                #current_owners = current_owners +  owner.owner.name + ", "
                i += 1
            else:
                break

        # Remove the last comma
        current_owners = current_owners[:-2]

        return(current_owners)

    def get_absolute_url(self):
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        return self.name + " // " + self.address

class PropertyOwner(models.Model):

    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    year = models.IntegerField()
    ownership_percent = models.IntegerField()

    def __str__(self):
        return self.owner.name + " // " + self.property.name + " // " + str(self.year)
