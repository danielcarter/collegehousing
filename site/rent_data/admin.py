from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadFileForm

from django.contrib.auth.models import Group, User

import np
import csv
import datetime
import dateutil.parser
import statistics
import math
import re
import chardet
from decimal import Decimal
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin

# Register models.
from rent_data.models import Property, PoliceReport, Owner, PropertyOwner, FireReport, Stat, RentObservation, Value, ManagementObservation


# Exports
class PropertyResource(resources.ModelResource):
    class Meta:
        model = Property

class OwnerResource(resources.ModelResource):
    class Meta:
        model = Owner

class PropertyOwnerResource(resources.ModelResource):
    class Meta:
        model = PropertyOwner

# Overwrite admin site so it can be extended.
class MyAdminSite(AdminSite):

    site_title="College Housing Project - San Marcos"
    site_header="College Housing Project - San Marcos"

    def import_menu(self, request):

        return render(request, 'admin/rent_data/import_menu.html')


        ############
        ## UTILITIES
        ############

    def get_urls(self):
        from django.conf.urls import url
        urls = super(MyAdminSite, self).get_urls()
        urls += [
            url(r'^rent_data/import_menu/$', self.admin_view(self.import_menu), name='import_menu'),
            url(r'^rent_data/reset_objects/$', self.admin_view(self.reset_objects), name='reset_objects'),
            url(r'^rent_data/clean_addresses/$', self.admin_view(self.clean_addresses), name='clean_addresses'),
            url(r'^rent_data/import_rent_observations/$', self.admin_view(self.import_rent_observations), name='import_rent_observations'),
            url(r'^rent_data/import_properties/$', self.admin_view(self.import_properties), name='import_properties'),
            url(r'^rent_data/import_police_reports/$', self.admin_view(self.import_police_reports), name='import_police_reports'),
            url(r'^rent_data/import_fire_reports/$', self.admin_view(self.import_fire_reports), name='import_fire_reports'),
            url(r'^rent_data/calculate_distances/$', self.admin_view(self.calculate_distances), name='calculate_distances'),

        ]
        return urls

    def reset_objects(self, request):

        Property.objects.all().delete()
        Owner.objects.all().delete()
        Value.objects.all().delete()
        RentObservation.objects.all().delete()
        FireReport.objects.all().delete()
        PoliceReport.objects.all().delete()
        PropertyOwner.objects.all().delete()

        return render(request, 'admin/rent_data/import_properties.html')

    def clean_addresses(self, request):

        for property in Property.objects.all():
            # Consolidate whitespace
            property.address = ' '.join(property.address.split())

            # Remove single characters (like 'w' in w river road)
            property.address = re.sub(r' \w{1} ', ' ', property.address)

            property.save()

        return render(request, 'admin/rent_data/import_properties.html')

    # Calculate distances is no longer used.
    def calculate_distances(self, request):

        ## This script gets run manually and should probably only be run on a local machine rather than on the server because it can be pretty slow. It needs to be modified each time so that we're only processing the new reports and not all the reports.

        #Edit these to select only the reports that you want to process.
        year = 2018 #used for saving stats
        start_date = datetime.date(2018, 1, 1)
        end_date = datetime.date(2018, 12, 31)

        import geopy.distance

        properties = Property.objects.all()

        police_reports = PoliceReport.objects.filter(date__range = (start_date, end_date))
        fire_reports = FireReport.objects.filter(date__range = (start_date, end_date))
        ems_reports = EMSReport.objects.filter(date__range = (start_date, end_date))

        i = 1

        # Lists used to calculate median values
        police_exact = []
        police_quarter = []
        police_half = []

        fire_exact = []
        fire_quarter = []
        fire_half = []

        ems_exact = []
        ems_quarter = []
        ems_half = []

        # For each property...
        for property in properties:
            tmp_coords_property = (property.latitude, property.longitude)

            i += 1
            print(i)

            # Integers used to count totals per property
            tmp_police_exact = 0
            tmp_police_quarter = 0
            tmp_police_half = 0

            tmp_fire_exact = 0
            tmp_fire_quarter = 0
            tmp_fire_half = 0

            tmp_ems_exact = 0
            tmp_ems_quarter = 0
            tmp_ems_half = 0

            # For each police report:
            for report in police_reports:

                tmp_coords_destination = (report.latitude, report.longitude)

                tmp_distance = geopy.distance.distance(tmp_coords_property, tmp_coords_destination).miles
                #print(tmp_distance)

                ## rewrite this part -- use new PropertyPoliceReports class

                if tmp_distance == 0:
                    property.policeReportsExact.add(report)
                    tmp_police_exact += 1
                    #print("exact")

                elif tmp_distance <= .25:
                    property.policeReportsQuarterMile.add(report)
                    tmp_police_quarter += 1
                    #print("quarter")

                elif tmp_distance <= .5:
                    property.policeReportsHalfMile.add(report)
                    tmp_police_half += 1
                    #print("half")

            # For each fire report:
            for report in fire_reports:

                tmp_coords_destination = (report.latitude, report.longitude)

                tmp_distance = geopy.distance.distance(tmp_coords_property, tmp_coords_destination).miles

                ## rewrite this part -- use new PropertyPoliceReports class

                if tmp_distance == 0:
                    property.fireReportsExact.add(report)
                    tmp_fire_exact += 1
                    #print("exact")

                elif tmp_distance <= .25:
                    property.fireReportsQuarterMile.add(report)
                    tmp_fire_quarter += 1
                    #print("quarter")

                elif tmp_distance <= .5:
                    property.fireReportsHalfMile.add(report)
                    tmp_fire_half += 1
                    #print("half")

            # For each fire report:
            for report in ems_reports:

                tmp_coords_destination = (report.latitude, report.longitude)

                tmp_distance = geopy.distance.distance(tmp_coords_property, tmp_coords_destination).miles

                ## rewrite this part -- use new PropertyPoliceReports class

                if tmp_distance == 0:
                    property.EMSReportsExact.add(report)
                    tmp_ems_exact += 1
                    #print("exact")

                elif tmp_distance <= .25:
                    property.EMSReportsQuarterMile.add(report)
                    tmp_ems_quarter += 1
                    #print("quarter")

                elif tmp_distance <= .5:
                    property.EMSReportsHalfMile.add(report)
                    tmp_ems_half += 1
                    #print("half")

            police_exact.append(tmp_police_exact)
            police_quarter.append(tmp_police_quarter + tmp_police_exact)
            police_half.append(tmp_police_half + tmp_police_quarter + tmp_police_exact)

            fire_exact.append(tmp_fire_exact)
            fire_quarter.append(tmp_fire_quarter + tmp_fire_exact)
            fire_half.append(tmp_fire_half + tmp_fire_quarter + tmp_fire_exact)

            ems_exact.append(tmp_ems_exact)
            ems_quarter.append(tmp_ems_quarter + tmp_ems_exact)
            ems_half.append(tmp_ems_half + tmp_ems_quarter + tmp_ems_exact)

        ## Save stats so we can compare ind. properties to distributions
        police_exact_q1, police_exact_q1_created = Stat.objects.update_or_create(
            name = "police_exact_q1",
            year = year
        )
        police_exact_q1.value = np.percentile(police_exact, 25)
        police_exact_q1.save()

        police_quarter_q1, police_quarter_q1_created = Stat.objects.update_or_create(
            name = "police_quarter_q1",
            year = year
        )
        police_quarter_q1.value = np.percentile(police_quarter, 25)
        police_quarter_q1.save()

        police_half_q1, police_half_q1_created = Stat.objects.update_or_create(
            name = "police_half_q1",
            year = year
        )
        police_half_q1.value = np.percentile(police_half, 25)
        police_half_q1.save()

        fire_exact_q1, fire_exact_q1_created = Stat.objects.update_or_create(
            name = "fire_exact_q1",
            year = year
        )
        fire_exact_q1.value = np.percentile(fire_exact, 25)
        fire_exact_q1.save()

        fire_quarter_q1, fire_quarter_q1_created = Stat.objects.update_or_create(
            name = "fire_quarter_q1",
            year = year
        )
        fire_quarter_q1.value = np.percentile(fire_quarter, 25)
        fire_quarter_q1.save()

        fire_half_q1, fire_half_q1_created = Stat.objects.update_or_create(
            name = "fire_half_q1",
            year = year
        )
        fire_half_q1.value = np.percentile(fire_half, 25)
        fire_half_q1.save()

        ems_exact_q1, ems_exact_q1_created = Stat.objects.update_or_create(
            name = "ems_exact_q1",
            year = year
        )
        ems_exact_q1.value = np.percentile(ems_exact, 25)
        ems_exact_q1.save()

        ems_quarter_q1, ems_quarter_q1_created = Stat.objects.update_or_create(
            name = "ems_quarter_q1",
            year = year
        )
        ems_quarter_q1.value = np.percentile(ems_quarter, 25)
        ems_quarter_q1.save()

        ems_half_q1, ems_half_q1_created = Stat.objects.update_or_create(
            name = "ems_half_q1",
            year = year
        )
        ems_half_q1.value = np.percentile(ems_half, 25)
        ems_half_q1.save()







        police_exact_q2, police_exact_q2_created = Stat.objects.update_or_create(
            name = "police_exact_q2",
            year = year
        )
        police_exact_q2.value = np.percentile(police_exact, 50)
        police_exact_q2.save()

        police_quarter_q2, police_quarter_q2_created = Stat.objects.update_or_create(
            name = "police_quarter_q2",
            year = year
        )
        police_quarter_q2.value = np.percentile(police_quarter, 50)
        police_quarter_q2.save()

        police_half_q2, police_half_q2_created = Stat.objects.update_or_create(
            name = "police_half_q2",
            year = year
        )
        police_half_q2.value = np.percentile(police_half, 50)
        police_half_q2.save()

        fire_exact_q2, fire_exact_q2_created = Stat.objects.update_or_create(
            name = "fire_exact_q2",
            year = year
        )
        fire_exact_q2.value = np.percentile(fire_exact, 50)
        fire_exact_q2.save()

        fire_quarter_q2, fire_quarter_q2_created = Stat.objects.update_or_create(
            name = "fire_quarter_q2",
            year = year
        )
        fire_quarter_q2.value = np.percentile(fire_quarter, 50)
        fire_quarter_q2.save()

        fire_half_q2, fire_half_q2_created = Stat.objects.update_or_create(
            name = "fire_half_q2",
            year = year
        )
        fire_half_q2.value = np.percentile(fire_half, 50)
        fire_half_q2.save()

        ems_exact_q2, ems_exact_q2_created = Stat.objects.update_or_create(
            name = "ems_exact_q2",
            year = year
        )
        ems_exact_q2.value = np.percentile(ems_exact, 50)
        ems_exact_q2.save()

        ems_quarter_q2, ems_quarter_q2_created = Stat.objects.update_or_create(
            name = "ems_quarter_q2",
            year = year
        )
        ems_quarter_q2.value = np.percentile(ems_quarter, 50)
        ems_quarter_q2.save()

        ems_half_q2, ems_half_q2_created = Stat.objects.update_or_create(
            name = "ems_half_q2",
            year = year
        )
        ems_half_q2.value = np.percentile(ems_half, 50)
        ems_half_q2.save()



        police_exact_q3, police_exact_q3_created = Stat.objects.update_or_create(
            name = "police_exact_q3",
            year = year
        )
        police_exact_q3.value = np.percentile(police_exact, 75)
        police_exact_q3.save()

        police_quarter_q3, police_quarter_q3_created = Stat.objects.update_or_create(
            name = "police_quarter_q3",
            year = year
        )
        police_quarter_q3.value = np.percentile(police_quarter, 75)
        police_quarter_q3.save()

        police_half_q3, police_half_q3_created = Stat.objects.update_or_create(
            name = "police_half_q3",
            year = year
        )
        police_half_q3.value = np.percentile(police_half, 75)
        police_half_q3.save()

        fire_exact_q3, fire_exact_q3_created = Stat.objects.update_or_create(
            name = "fire_exact_q3",
            year = year
        )
        fire_exact_q3.value = np.percentile(fire_exact, 75)
        fire_exact_q3.save()

        fire_quarter_q3, fire_quarter_q3_created = Stat.objects.update_or_create(
            name = "fire_quarter_q3",
            year = year
        )
        fire_quarter_q3.value = np.percentile(fire_quarter, 75)
        fire_quarter_q3.save()

        fire_half_q3, fire_half_q3_created = Stat.objects.update_or_create(
            name = "fire_half_q3",
            year = year
        )
        fire_half_q3.value = np.percentile(fire_half, 75)
        fire_half_q3.save()

        ems_exact_q3, ems_exact_q3_created = Stat.objects.update_or_create(
            name = "ems_exact_q3",
            year = year
        )
        ems_exact_q3.value = np.percentile(ems_exact, 75)
        ems_exact_q3.save()

        ems_quarter_q3, ems_quarter_q3_created = Stat.objects.update_or_create(
            name = "ems_quarter_q3",
            year = year
        )
        ems_quarter_q3.value = np.percentile(ems_quarter, 75)
        ems_quarter_q3.save()

        ems_half_q3, ems_half_q3_created = Stat.objects.update_or_create(
            name = "ems_half_q3",
            year = year
        )
        ems_half_q3.value = np.percentile(ems_half, 75)
        ems_half_q3.save()



        context = {
        }

        return render(request, 'admin/rent_data/calculate_distances.html', context=context)

    def import_properties(self, request):

        if request.method == 'POST':

            report = {
                'total_records': 0,
                'new_properties': 0,
                'new_coordinates': 0,
                'new_names': 0
            }

            form = UploadFileForm(request.POST,request.FILES)
            if form.is_valid():
                file = request.FILES['file']
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                for row in reader:

                    try:
                        print(row['year_built'])
                    except:
                        print("No Year")

                    # If property exists, check the details...
                    try:
                        tmp_property = Property.objects.get(address = row['address_canonical'])
                        report['total_records'] += 1

                        try:
                            if row['year_built'] is not None:
                                print(row['year_built'])
                                tmp_property.year_built = int(row['year_built'])
                                tmp_property.save()

                        except:
                            print("Record exists. Not updating year built.")

                    # Otherwise, insert a new property.
                    except:
                        tmp_property = Property(
                            address = row['address_canonical'],
                            latitude = row['latitude'],
                            longitude = row['longitude'],
                            name = row['property_name']
                        )
                        tmp_property.save()
                        report['new_properties'] += 1
                        report['total_records'] += 1

                    # RELATIONSHIPS

                    tmp_owner, tmp_owner_created = Owner.objects.get_or_create(
                        name = row['owner_name']
                    )
                    tmp_owner.address1 = row['owner_address_1']
                    tmp_owner.address2 = row['owner_address_2']
                    tmp_owner.address3 = row['owner_address_3']
                    tmp_owner.city = row['owner_city']
                    tmp_owner.state = row['owner_state']
                    tmp_owner.zip = row['owner_zip']

                    tmp_owner.save()

                    tmp_property_owner, tmp_property_owner_created = PropertyOwner.objects.get_or_create(
                        owner = tmp_owner,
                        property = tmp_property,
                        year = row['year'],
                        ownership_percent = row['ownership_percent'],
                    )

                    tmp_property_owner.save()

                    tmp_value, tmp_value_created = Value.objects.get_or_create(
                        value = row['value'],
                        year = row['year'],
                    )

                    tmp_value.save()

                    tmp_property.values.add(tmp_value)
                    tmp_property.save()

                context = {
                    'report': report
                }

                return render(request, 'admin/rent_data/import_properties_report.html', context=context)
            else:
                form = UploadFileForm()
                context = {
                    'form': form
                }
                return render(request, 'admin/rent_data/import_properties.html', context=context)

        else:
            form = UploadFileForm()
            context = {
                'form': form
            }
            return render(request, 'admin/rent_data/import_properties.html', context=context)

    def import_rent_observations(self, request):

        if request.method == 'POST':

            report = {
                'total_records': 0
            }

            form = UploadFileForm(request.POST,request.FILES)
            if form.is_valid():
                file = request.FILES['file']
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                for row in reader:

                    tmp_property = Property.objects.get(address = row['address'])

                    # Update things we always update
                    if row['act_ally'] is not "":
                        tmp_property.act_ally = row['act_ally']
                    if row['lease_type'] is not "":
                        tmp_property.lease_type = row['lease_type']
                    if row['units'] is not "":
                        tmp_property.units = float(row['units'])
                    if row['beds'] is not "":
                        tmp_property.beds = float(row['beds'])
                    tmp_property.save()


                    # Create a new management observation
                    tmp_management_observation, tmp_management_observation_create = ManagementObservation.objects.get_or_create(
                        company = row['management_company'],
                        date = datetime.datetime.strptime(str(row['observation_date']), "%m/%d/%y").date()
                    )

                    tmp_property.management_companies.add(tmp_management_observation)

                    # Create all the rent observations....
                    if row['rent_1bdr'] is not "" and row['sqft_1bdr'] is not "":
                        tmp_rent_observation, tmp_rent_observation_created = RentObservation.objects.get_or_create(
                            bedrooms = 1,
                            rent = math.floor(float(row['rent_1bdr'])),
                            sqft = math.floor(float(row['sqft_1bdr'])),
                            date = datetime.datetime.strptime(str(row['observation_date']), "%m/%d/%y").date()
                        )
                        tmp_property.rents.add(tmp_rent_observation)

                    if row['rent_2bdr'] is not "" and row['sqft_2bdr'] is not "":
                        tmp_rent_observation, tmp_rent_observation_created = RentObservation.objects.get_or_create(
                            bedrooms = 2,
                            rent = math.floor(float(row['rent_2bdr'])),
                            sqft = math.floor(float(row['sqft_2bdr'])),
                            date = datetime.datetime.strptime(str(row['observation_date']), "%m/%d/%y").date()
                        )
                        tmp_property.rents.add(tmp_rent_observation)

                    if row['rent_3bdr'] is not "" and row['sqft_3bdr'] is not "":
                        tmp_rent_observation, tmp_rent_observation_created = RentObservation.objects.get_or_create(
                            bedrooms = 3,
                            rent = math.floor(float(row['rent_3bdr'])),
                            sqft = math.floor(float(row['sqft_3bdr'])),
                            date = datetime.datetime.strptime(str(row['observation_date']), "%m/%d/%y").date()
                        )
                        tmp_property.rents.add(tmp_rent_observation)

                    if row['rent_4bdr'] is not "" and row['sqft_4bdr'] is not "":
                        tmp_rent_observation, tmp_rent_observation_created = RentObservation.objects.get_or_create(
                            bedrooms = 4,
                            rent = math.floor(float(row['rent_4bdr'])),
                            sqft = math.floor(float(row['sqft_4bdr'])),
                            date = datetime.datetime.strptime(str(row['observation_date']), "%m/%d/%y").date()
                        )
                        tmp_property.rents.add(tmp_rent_observation)

                    if row['rent_5bdr'] is not "" and row['sqft_5bdr'] is not "":
                        tmp_rent_observation, tmp_rent_observation_created = RentObservation.objects.get_or_create(
                            bedrooms = 5,
                            rent = math.floor(float(row['rent_5bdr'])),
                            sqft = math.floor(float(row['sqft_5bdr'])),
                            date = datetime.datetime.strptime(str(row['observation_date']), "%m/%d/%y").date()
                        )
                        tmp_property.rents.add(tmp_rent_observation)

                    if row['rent_6bdr'] is not "" and row['sqft_6bdr'] is not "":
                        tmp_rent_observation, tmp_rent_observation_created = RentObservation.objects.get_or_create(
                            bedrooms = 6,
                            rent = math.floor(float(row['rent_6bdr'])),
                            sqft = math.floor(float(row['sqft_6bdr'])),
                            date = datetime.datetime.strptime(str(row['observation_date']), "%m/%d/%y").date()
                        )
                        tmp_property.rents.add(tmp_rent_observation)

                context = {
                    'report': report
                }

                return render(request, 'admin/rent_data/import_rent_observations.html', context=context)
            else:
                form = UploadFileForm()
                context = {
                    'form': form
                }
                return render(request, 'admin/rent_data/import_rent_observations.html', context=context)

        else:
            form = UploadFileForm()
            context = {
                'form': form
            }
            return render(request, 'admin/rent_data/import_rent_observations.html', context=context)

    def import_police_reports(self, request):

        #PoliceReport.objects.all().delete()

        if request.method == 'POST':

            report = {
                'total_records': 0,
                'total_records_created': 0,
            }

            form = UploadFileForm(request.POST,request.FILES)

            if form.is_valid():

                file = request.FILES['file']
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                for row in reader:

                    report['total_records'] += 1

                    tmp_address = re.sub(r'#.*$', "", row['Location']).strip().upper()
                    tmp_address = re.sub(r' \w{1} ', ' ', tmp_address)
                    tmp_address = tmp_address + ", SAN MARCOS, TX 78666"
                    tmp_address = ' '.join(tmp_address.split())

                    print(row['TimeReported'])

                    #tmp_date = datetime.datetime.strptime(row['TimeReported'], '%m/%d/%Y %H:%M:%S %p')
                    tmp_date = dateutil.parser.parse(row['TimeReported'])

                    try:
                        tmp_property = Property.objects.get(address = tmp_address)

                        tmp_report, tmp_report_created = PoliceReport.objects.get_or_create(
                            date = tmp_date,
                            activity = row['Activity'],
                            disposition = row['Disposition']
                        )

                        tmp_property.police_reports.add(tmp_report)

                        if tmp_report_created:
                            report['total_records_created'] += 1

                    except Exception as e:
                        print(e)

                context = {
                    'report': report
                }

                return render(request, 'admin/rent_data/import_police_reports_report.html', context=context)
            else:
                form = UploadFileForm()
                context = {
                    'form': form
                }
                return render(request, 'admin/rent_data/import_police_reports.html', context=context)

        else:
            form = UploadFileForm()
            context = {
                'form': form
            }
            return render(request, 'admin/rent_data/import_police_reports.html', context=context)

    def import_fire_reports(self, request):

        #FireReport.objects.all().delete()

        #import logging
        #logging.basicConfig(filename='fire_reports_bad.log',level=logging.DEBUG)

        if request.method == 'POST':

            report = {
                'total_records': 0,
                'total_records_created': 0,
            }

            form = UploadFileForm(request.POST,request.FILES)

            if form.is_valid():

                file = request.FILES['file']
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                for row in reader:

                    report['total_records'] += 1

                    tmp_address = re.sub(r'#.*$', "", row['Address']).strip().upper()
                    tmp_address = re.sub(r' \w{1} ', ' ', tmp_address)
                    tmp_address = tmp_address + ", SAN MARCOS, TX 78666"
                    tmp_address = ' '.join(tmp_address.split())
                    #print(tmp_address)

                    tmp_ems = False

                    try:
                        tmp_property = Property.objects.get(address = tmp_address)
                        tmp_date = dateutil.parser.parse(row['Date'])

                        if re.match(r'^EMS', row['Description']):
                            tmp_ems = True

                        tmp_report, tmp_report_created = FireReport.objects.get_or_create(
                            ems = tmp_ems,
                            date = tmp_date,
                            description = row['Description']
                        )

                        tmp_property.fire_reports.add(tmp_report)

                        if tmp_report_created:
                            report['total_records_created'] += 1

                    except Exception as e:

                        #logging.debug(tmp_address)
                        print(e)

                context = {
                    'report': report
                }

                return render(request, 'admin/rent_data/import_fire_reports_report.html', context=context)
            else:
                form = UploadFileForm()
                context = {
                    'form': form
                }
                return render(request, 'admin/rent_data/import_police_reports.html', context=context)

        else:
            form = UploadFileForm()
            context = {
                'form': form
            }
            return render(request, 'admin/rent_data/import_fire_reports.html', context=context)

admin_site = MyAdminSite()

# Add models to interface.
@admin.register(User, site=admin_site)
@admin.register(Group, site=admin_site)


@admin.register(Property, site=admin_site)
class PropertyAdmin(ImportExportActionModelAdmin):
    fields = ('address','name', 'year_built', 'section_8', 'management_companies', 'notes','rents')
    search_fields = ['address','name']
    pass

@admin.register(RentObservation, site=admin_site)
class RentObservationAdmin(admin.ModelAdmin):
    pass

@admin.register(PoliceReport, site=admin_site)
class PoliceReportAdmin(admin.ModelAdmin):
    pass

@admin.register(FireReport, site=admin_site)
class FireReportAdmin(admin.ModelAdmin):
    pass

@admin.register(Owner, site=admin_site)
class OwnerAdmin(ImportExportActionModelAdmin):
    pass

@admin.register(PropertyOwner, site=admin_site)
class PropertyOwnerAdmin(ImportExportActionModelAdmin):
    list_filter = ('year','owner')
    pass

@admin.register(Stat, site=admin_site)
class StatAdmin(admin.ModelAdmin):
    pass
