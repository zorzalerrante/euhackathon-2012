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

def render_json(request, data):
    return render_to_response('json.html', {'json': json.dumps(data)}, context_instance=RequestContext(request), mimetype='application/json')

def add_user_time(request):
    user_id = request.GET['userId']
    user = get_object_or_404(User, uid=user_id)
    
    user.allowed_time += int(request.GET['additionalTime'])
    user.save()
    return render_json(request, {'userId': user.uid, 'allowedTime': user.allowed_time})
    
def user_time(request):
    user_id = request.GET['userId']
    
    user, created = User.objects.get_or_create(uid=user_id)

    print request.GET
    
    try:
        prev_url = request.GET['previousUrl']
        spent = int(request.GET['previousTimeSpent'])
        
        user.allowed_time -= spent 
        
        if user.allowed_time < 0:
            user.allowed_time = 0
        
        user.save()
        
        if prev_url:
            prev_site, created = Site.objects.get_or_create(url=prev_url)
            activity = Activity(user=user, site=prev_site, seconds=spent)
            activity.save()
        
            
    except KeyError:
        pass
        
   
    
    try:
        url = request.GET['currentUrl']
    except KeyError:
        url = None
    
    if url:
        curr_site, created = Site.objects.get_or_create(url=url)
        
        allowed = user.allowed_time
        
        if curr_site.score < 0:
            allowed = allowed / 2
        
        data = {'timeLeft': allowed}
    else:
        data = {'timeLeft': float('Infinity')}
    
    return render_json(request, data)

def user_dash(request, user_id):
    user = get_object_or_404(User, uid=user_id)
    data = {}
    
    start_date = datetime.date.today()
    final_date = start_date - datetime.timedelta(days=14)
    
    counts = []
    
    user_activities = user.activity_set
    
    for i in xrange(0, 15):
        date = start_date - datetime.timedelta(days=i)
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
    
    
    data['sites'] = list(user_activities.filter(datetime__gte=final_date).values('site__url', 'site__score').annotate(milliseconds=Sum('seconds')).order_by('-milliseconds')[:10])
    
    print data
    return render_json(request, data)