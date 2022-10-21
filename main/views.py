from django.shortcuts import render
import pygeoip
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PacketModel
from ipwhois import IPWhois
from django.db.models import Q

def most_popular_desc():
    packets = PacketModel.objects.filter(clientID=1)
    packets = packets.filter(~Q(description = "Не удалось найти информацию о компании"))
    popular = {}
    for i in range(len(packets)):
        if packets[i].description not in popular:
            popular[packets[i].description] = 0
            for j in range(len(packets)):
                if packets[i].description == packets[j].description:
                    popular[packets[i].description] += 1
        else:
            continue
    value = ""
    max = 0
    for i in range(len(popular)):
        if popular[packets[i].description] >= max:
            max = popular[packets[i].description]
            value = packets[i].description
    return value


def most_popular_country():
    packets = PacketModel.objects.filter(clientID=1)
    packets = packets.filter(~Q(country="Не удалось определить местоположение"))
    popular = {}

    for i in range(len(packets)):
        if packets[i].country not in popular:
            popular[packets[i].country] = 0
            for j in range(len(packets)):
                if packets[i].country == packets[j].country:
                    popular[packets[i].country] += 1
        else:
            continue
    value = ""
    max = 0
    for i in range(len(popular)):
        if popular[packets[i].country] >= max:
            max = popular[packets[i].country]
            value = packets[i].country
    return value


def index(request):
    return render(request,'index.html')


def geo_result(request):
    if request.method == 'POST':
        ip = request.POST.get("ip")
        gi = pygeoip.GeoIP('config/GeoLiteCity.dat')
        try:
            rec = gi.record_by_name(ip)
            city = rec['city']
            country = rec['country_name']
            longitude = rec['longitude']
            lat = rec['latitude']
            adress = 'Address: ' + ip + ' Geo-located:  ' + str(city) + ', ' + str(country) + ' Latitude: ' + str(lat) + ', Longitude: ' + str(longitude)
            url = "https://static-maps.yandex.ru/1.x/?ll="+str(longitude)+","+str(lat)+"4&size=650,450&z=14&l=map&pt="+str(longitude)+","+str(lat)+",pmwtm1~37.64,55.76363,pmwtm99"
            clickUrl = "https://yandex.ru/maps//?ll="+str(longitude)+"%2C"+str(lat)+"&z=14"
            return render(request,"sucsess_geo.html",context={'adress': adress,'url':url,'clickUrl':clickUrl})
        except:
            return render(request,'fail_geo.html')


def clients(request):
    last_ten = PacketModel.objects.filter(clientID=1).order_by('-id')[:40]
    for i in range(len(last_ten)):
        print(last_ten[i].info())
    popular_country = most_popular_country()
    popular_desc = most_popular_desc()
    return render(request,'clients.html', {'packets':last_ten,'popular_country':popular_country,"popular_desc":popular_desc})


def geo_view(request):
    return render(request,'geo.html')


@api_view(["POST"])
def get_packets(request):
    # print(request.data.get('clientID'))
    # print(request.data.get('data'))
    # print(request.data.get('country'))
    packet = PacketModel()
    try:
        gi = pygeoip.GeoIP('config/GeoLiteCity.dat')
        rec = gi.record_by_name(request.data.get('country'))
        country = rec['country_name']
        packet.country = country
    except:
        packet.country = "Не удалось определить местоположение"
    try:
        obj = IPWhois(request.data.get('country'))
        res = obj.lookup_whois(request.data.get('country'))
        description = res["nets"][0]['name']
        packet.description = description
    except:
        packet.description = "Не удалось найти информацию о компании"
    packet.clientID = request.data.get('clientID')
    packet.data = request.data.get('data')
    packet.save()
    return Response('ok')