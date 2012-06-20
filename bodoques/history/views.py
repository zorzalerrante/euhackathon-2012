from django.template import Context, loader
from models import *
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.core.cache import cache
from django.template import RequestContext
from django.utils.html import strip_tags
from django.db.models import Q
from django.core import serializers
import json 

def render_json(request, data):
    return render_to_response('json.html', {'json': json.dumps(data)}, context_instance=RequestContext(request), mimetype='application/json')

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
        data = {'timeLeft': 'Infinity'}
    
    return render_json(request, data)
