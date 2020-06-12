from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.db.models import Min, Count
from django.urls import reverse

import csv
import datetime
import re

from rent_data.models import Property, Owner, PropertyOwner, Stat, Value, ManagementObservation, FireReport, PoliceReport, RentObservation

# Create your views here.
def index(request):

    properties = Property.objects.all()

    context = {
        'page_title': 'College Housing Project',
        'properties': properties
    }

    return render(request, 'index.html', context=context)

def about(request):

    context = {
        'page_title': 'About',
    }

    return render(request, 'about.html', context=context)

def process(request):

    context = {
        'page_title': 'Process and Data',
    }

    return render(request, 'process.html', context=context)

def tutorials(request):

    context = {
        'page_title': 'Tutorials',
    }

    return render(request, 'tutorials.html', context=context)

def reports(request):

    context = {
        'page_title': 'Reports',
    }

    return render(request, 'reports.html', context=context)

def property(request, id):

    property = Property.objects.get(pk=id)

    # Rent
    if property.current_2bdrm_rent is not "unknown":
        median_rent = Stat.objects.get(name__exact = "median_2bdr_rent").value
    else:
        median_rent = None

    # Police
    police_reports = property.police_reports.all()

    # List and sort all the police activities
    police_activities = {}
    for report in police_reports:
        if (report.activity not in police_activities):
            police_activities[report.activity] = 1
        else:
            police_activities[report.activity] += 1

    police_activities_ordered = sorted(police_activities, key=police_activities.get, reverse=True)

    top_activities = police_activities_ordered[0:3]

    top_activities_w_other = top_activities + ["Other"]

    police_report_years = []
    for report in police_reports:
        if report.date.year not in police_report_years:
            police_report_years.append(report.date.year)
    police_report_years.sort()

    police_reports_data = {}
    for activity in top_activities_w_other:
        police_reports_data[activity] = {}
        for year in police_report_years:
            if (activity == "Other"):
                tmp_reports = police_reports.filter(date__year = year).exclude(activity__in = top_activities)
            else:
                tmp_reports = police_reports.filter(date__year = year, activity__exact = activity)
            police_reports_data[activity][year] = tmp_reports.count()


    # Fire
    fire_reports = property.fire_reports.all().filter(ems__exact=False)

    fire_report_years = []
    for report in fire_reports:
        if report.date.year not in fire_report_years:
            fire_report_years.append(report.date.year)
    fire_report_years.sort()

    fire_reports_data = {}
    for year in fire_report_years:
        tmp_reports = fire_reports.filter(date__year = year)
        fire_reports_data[year] = tmp_reports.count()


    # EMS
    ems_reports = property.fire_reports.all().filter(ems__exact=True)

    ems_report_years = []
    for report in ems_reports:
        if report.date.year not in ems_report_years:
            ems_report_years.append(report.date.year)
    ems_report_years.sort()

    ems_reports_data = {}
    for year in ems_report_years:
        tmp_reports = ems_reports.filter(date__year = year)
        ems_reports_data[year] = tmp_reports.count()



    context = {
        'page_title': property.name,
        'hide_title': True,
        'body_class': 'property-single',
        'property': property,
        'fire_reports_data': fire_reports_data,
        'police_reports_data': police_reports_data,
        'ems_reports_data': ems_reports_data,
        'police_report_years': police_report_years,
        'median_rent': median_rent,
        'values': property.values.order_by('year')
    }

    return render(request, 'property.html', context=context)

def owners(request):

    owners = Owner.objects.all().order_by('name')

    context = {
        'page_title': "All Property Owners",
        'owners': owners,
        'body_class': 'owners'
    }

    return render(request, 'owners.html', context=context)

def owner(request, id):

    owner = Owner.objects.get(pk=id)

    ## This is a mess.. need to figure out these complex through filters....

    ownership_observations = PropertyOwner.objects.filter(owner = owner).order_by("-year")

    years = []
    ownerships = []
    properties = []

    for observation in ownership_observations:
        years.append(observation.year)
        properties.append(observation.property)

    properties = set(properties)

    for property in properties:

        for year in range(min(years), max(years) + 1):

            tmp_ownerships = ownership_observations.all().filter(property__pk = property.id)

            tmp_ownerships = tmp_ownerships.all().filter(year__exact = year)

            tmp_value = property.values.all().get(year__exact = year).value

            ownerships.append(
                {
                    'property': property,
                    'year': year,
                    'value': tmp_value,
                    'ownership_percent': observation.ownership_percent
                }
            )

    year_value_data = []

    for year in range(min(years), max(years) + 1):

        tmp_ownerships = ownership_observations.all().filter(year__exact = year)

        tmp_total_value = 0
        for observation in tmp_ownerships:
            tmp_total_value += (observation.property.values.all().get(year__exact = year).value * observation.ownership_percent / 100)

        year_value_data.append(
            {
                'year': year,
                'total_value': tmp_total_value
            }
        )


    context = {
        'page_title': owner.name,
        'hide_title': True,
        'body_class': 'owner-single',
        'owner': owner,
        'properties': properties,
        'ownership_observations': ownerships,
        'year_value_data': year_value_data
    }

    return render(request, 'owner.html', context=context)

def properties(request):

    properties = Property.objects.all().order_by('name')

    context = {
        'page_title': 'All Properties',
        'properties': properties,
        'body_class': 'properties'
    }

    return render(request, 'properties.html', context=context)

def analysis(request):


    context = {
        'page_title': 'Analysis',
        'body_class': 'analysis'
    }

    return render(request, 'analysis.html', context=context)


###########
## EXPORTS
###########

def export_properties(request):

    latest_value_year = Value.objects.order_by("-year")[0].year

    response = HttpResponse(content_type='text/csv')

    filename = str(datetime.date.today()) + "_San_Marcos_Apartment_Summary.csv"

    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    writer = csv.writer(response)

    writer.writerow(['Address', 'Property Name', 'Year Built', 'ACT Ally', 'Section 8', 'Value', 'Owners', 'Management Company', '1 Bed Rent', '1 Bed Square Feet', '2 Bed Rent', '2 Bed Square Feet', '3 Bed Rent', '3 Bed Square Feet', '4 Bed Rent', '4 Bed Square Feet', '5 Bed Rent', '5 Bed Square Feet', '6 Bed Rent', '6 Bed Square Feet'])

    properties = Property.objects.all()

    for property in properties:

        propertyOwnerSet = PropertyOwner.objects.filter(property = property, year = latest_value_year)
        owners = ""
        for propertyOwner in propertyOwnerSet:
            owners = owners + propertyOwner.owner.name + ", "

        writer.writerow([
            property.address,
            property.name,
            property.year_built,
            property.act_ally,
            property.section_8,
            property.values.filter(year = latest_value_year).values_list('value', flat=True).first(),
            owners[:-2],
            property.management_companies.order_by('-date').values_list('company', flat=True).first(),
            property.rents.filter(bedrooms = 1).order_by('-date').values_list('rent', flat=True).first(),
            property.rents.filter(bedrooms = 1).order_by('-date').values_list('sqft', flat=True).first(),
            property.rents.filter(bedrooms = 2).order_by('-date').values_list('rent', flat=True).first(),
            property.rents.filter(bedrooms = 2).order_by('-date').values_list('sqft', flat=True).first(),
            property.rents.filter(bedrooms = 3).order_by('-date').values_list('rent', flat=True).first(),
            property.rents.filter(bedrooms = 3).order_by('-date').values_list('sqft', flat=True).first(),
            property.rents.filter(bedrooms = 4).order_by('-date').values_list('rent', flat=True).first(),
            property.rents.filter(bedrooms = 4).order_by('-date').values_list('sqft', flat=True).first(),
            property.rents.filter(bedrooms = 5).order_by('-date').values_list('rent', flat=True).first(),
            property.rents.filter(bedrooms = 5).order_by('-date').values_list('sqft', flat=True).first(),
            property.rents.filter(bedrooms = 6).order_by('-date').values_list('rent', flat=True).first(),
            property.rents.filter(bedrooms = 6).order_by('-date').values_list('sqft', flat=True).first(),
        ])

    return response

def export_fire_reports(request, id=None):

    response = HttpResponse(content_type='text/csv')

    if id is not None:
        property = Property.objects.get(pk=id)
        reports = property.fire_reports.all()
        tmp_string = "".join([c for c in property.address if re.match(r'\w', c)])
        filename = str(datetime.date.today()) + "_" + tmp_string + "_Fire_EMS_Reports.csv"
    else:
        reports = FireReport.objects.all()
        filename = str(datetime.date.today()) + "_San_Marcos_Apartment_Fire_EMS_Reports.csv"


    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    writer = csv.writer(response)

    writer.writerow(['Date','Property','Address','Section 8','ACT Ally','EMS','Description'])

    for report in reports:

        property = report.property_set.first()

        writer.writerow([
            report.date,
            property.name,
            property.address,
            property.section_8,
            property.act_ally,
            report.ems,
            report.description,
        ])

    return response

def export_police_reports(request, id=None):

    response = HttpResponse(content_type='text/csv')

    if id is not None:
        property = Property.objects.get(pk=id)
        reports = property.police_reports.all()
        tmp_string = "".join([c for c in property.address if re.match(r'\w', c)])
        filename = str(datetime.date.today()) + "_" + tmp_string + "_Police_Reports.csv"
    else:
        reports = PoliceReport.objects.all()
        filename = str(datetime.date.today()) + "_San_Marcos_Apartment_Police_Reports.csv"

    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    writer = csv.writer(response)

    writer.writerow(['Date','Property','Address','Section 8','ACT Ally','Activity','Disposition'])


    for report in reports:

        property = report.property_set.first()

        writer.writerow([
            report.date,
            property.name,
            property.address,
            property.section_8,
            property.act_ally,
            report.activity,
            report.disposition,
        ])

    return response
