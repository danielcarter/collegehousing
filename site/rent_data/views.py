from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.db.models import Min, Count
from django.urls import reverse

import csv
import datetime

from rent_data.models import Property, Owner, PropertyOwner, Stat, Value, ManagementObservation, FireReport, PoliceReport

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


def reports(request):

    context = {
        'page_title': 'Reports',
    }

    return render(request, 'reports.html', context=context)


def property(request, id):

    property = Property.objects.get(pk=id)

    all_owners = PropertyOwner.objects.filter(property = property).order_by("-year")
    current_owners = ""
    latest_year = 0

    i = 0
    for owner in all_owners:
        print(latest_year)
        if owner.year >= latest_year:
            latest_year = owner.year
            ## Used to link this ...
            #current_owners = current_owners + "<a href='" + reverse('owner', args=[owner.owner.id]) + "' title='Ownership Information for " + owner.owner.name + "'>" + owner.owner.name + "</a>, "

            current_owners = current_owners +  owner.owner.name + ", "
            i += 1
        else:
            break

    if i > 1:
        current_owners = "Owners: " + current_owners
    else:
        current_owners = "Owner: " + current_owners

    # Remove the last comma
    current_owners = current_owners[:-2]

    property_value = property.values.all().order_by("-year")[0].value

    context = {
        'page_title': property.name,
        'body_class': 'property-single',
        'property': property,
        'property_value': property_value,
        'all_owners': all_owners,
        'current_owners': current_owners,
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

    owner = Owner.objects.filter(pk=id)

    ## This is a mess.. need to figure out these complex through filters....

    ownership_observations = PropertyOwner.objects.filter(owner = owner[0]).order_by("-year")

    context = {
        'page_title': owner[0].name,
        'owner': owner[0],
        'ownership_observations': ownership_observations,
        'body_class': 'owner-single'
    }

    return render(request, 'owner.html', context=context)

def properties(request):

    properties = Property.objects.all().order_by('address')

    context = {
        'page_title': 'Property Data',
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

def export_fire_reports(request):

    response = HttpResponse(content_type='text/csv')

    filename = str(datetime.date.today()) + "_San_Marcos_Apartment_Fire_Reports.csv"

    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    writer = csv.writer(response)

    writer.writerow(['Date','Property','Address','Section 8','ACT Ally','EMS','Description'])

    reports = FireReport.objects.all()

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

def export_police_reports(request):

    response = HttpResponse(content_type='text/csv')

    filename = str(datetime.date.today()) + "_San_Marcos_Apartment_Police_Reports.csv"

    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    writer = csv.writer(response)

    writer.writerow(['Date','Property','Address','Section 8','ACT Ally','Activity','Disposition'])

    reports = PoliceReport.objects.all()

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
