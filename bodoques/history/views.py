from django.template import Context, loader
from models import *
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.core.cache import cache
from django.template import RequestContext
from django.utils.html import strip_tags
from django.db.models import Q, Sum, Avg
from django.core import serializers
import json 
import datetime
from urlparse import urlparse

def get_site_from_url(site):
    if not site.startswith('http'):
        site = 'http://' + site
    return urlparse(site).hostname


def render_json(request, data):
    return render_to_response('json.html', {'json': json.dumps(data)}, context_instance=RequestContext(request), mimetype='application/json')

def add_user_time(request):
    user_id = request.GET['userId']
    user = get_object_or_404(User, uid=user_id)
    
    time = int(request.GET['additionalTime'])
    
    if time != 0:
        user.allowed_time += time
        user.save()
        
    return render_json(request, {'userId': user.uid, 'allowedTime': user.allowed_time / (60 * 1000)})
    
def user_time(request):
    user_id = request.GET['userId']
    
    user, created = User.objects.get_or_create(uid=user_id)

    print request.GET
    
    try:
        prev_url = get_site_from_url(request.GET['previousUrl'])
        spent = int(request.GET['previousTimeSpent'])
        
        user.allowed_time -= spent 
        
        if user.allowed_time < 0:
            user.allowed_time = 0
        
        user.save()
        
        if prev_url and spent > 0:
            prev_site, created = Site.objects.get_or_create(url=prev_url)
            activity = Activity(user=user, site=prev_site, seconds=spent)
            activity.save()
            
    except KeyError:
        pass
        
   
    
    try:
        url = get_site_from_url(request.GET['currentUrl'])
    except KeyError:
        url = None
    
    if url:
        curr_site, created = Site.objects.get_or_create(url=url)
        
        allowed = user.allowed_time
        
        if curr_site.score < 0:
            allowed = allowed / 2
        
        data = {'userId': user.uid, 'timeLeft': allowed, 'currentSiteType': curr_site.score}
    else:
        data = {'userId': user.uid, 'timeLeft': 'Infinity', 'currentSiteType': None}
    
    return render_json(request, data)

def user_dash(request, user_id):
    user = get_object_or_404(User, uid=user_id)
    data = {'user_id': user_id, 'name': user.name, 'time_left': user.allowed_time / (1000 * 60) }
    
    final_date = datetime.date.today()
    start_date = final_date - datetime.timedelta(days=14)
    
    counts = []
    
    user_activities = user.activity_set
    
    for i in xrange(0, 15):
        date = start_date + datetime.timedelta(days=i)
        activities = user_activities.filter(datetime__day=date.day, datetime__year=date.year, datetime__month=date.month)
        good = activities.filter(site__score=1).aggregate(Sum('seconds'), Avg('seconds'))
        bad = activities.filter(site__score=-1).aggregate(Sum('seconds'), Avg('seconds'))
        
        count = {
            'date': date.isoformat(), 
            'good': {'avg': 0, 'sum': 0}, 
            'bad': {'avg': 0, 'sum': 0},
        }
        
        if good['seconds__sum']:
            count['good']['sum'] = good['seconds__sum'] / 1000
            
        if good['seconds__avg']:
            count['good']['avg'] = good['seconds__avg'] / 1000

        if bad['seconds__sum']:
            count['bad']['sum'] = bad['seconds__sum'] / 1000

        if bad['seconds__avg']:
            count['bad']['avg'] = bad['seconds__avg'] / 1000
            
        counts.append(count)
    
    data['counts'] = counts
    
    
    data['sites'] = list(user_activities.filter(datetime__gte=start_date).values('site__url', 'site__score').annotate(milliseconds=Sum('seconds')).order_by('-milliseconds')[:10])
    
    print data
    return render_json(request, data)
    
def global_sites(request):
    most_visited = Site.objects.values('url', 'score').annotate(total_time=Sum('activity__seconds')).exclude(total_time=None).filter(total_time__gt=0)
    return render_json(request, list(most_visited))