""" This file contains functionality to handle OSIS urls. """

import mariqt.variables as miqtv
import mariqt.core as miqtc
import requests
import json


def getOsisEventUrl(expedition_id:int, event_name:str):
        """ Returns osis event url if osis event id can be successfully retrieved from event_name.
        Returns "" if not successsful. """
        event_url = ""
        event_ids = getExpeditionEventIds(expedition_id)

        event_name_options = [event_name]
        event_name_options.append(event_name)
        # e.g. M182_040-1_XOFOS
        name_split = event_name.split('_')
        if len(name_split) >= 2:
            event_name_options.append(name_split[1])
        # e.g. MSM96_003_AUV-01
        if len(name_split) >= 3:
            ext_split = name_split[2].split('-')
            if len(ext_split) == 2:
                event_name_options.append(name_split[1] + '-' + ext_split[1])
        event_name_options_0strip = []
        for name in event_name_options:
            dash_split = name.split('-')
            event_name_options_0strip.append('-'.join([e.lstrip('0') for e in dash_split]))
        event_name_options += event_name_options_0strip
        for event_name in event_name_options:
            if event_name in event_ids:
                event_url = getEventUrl(expedition_id,event_ids[event_name])
                break
        
        return event_url


def getExpeditionEventIds(expedition_id:int):
    """ returns dict {event_name: event_id} """
    ret = {}
    try:
        res = requests.get(miqtv.apis['osis_underway'] + 'expeditions/' + str(expedition_id) + '/events', timeout=5)
    except requests.exceptions.ConnectionError:
        res = False

    if not res:
        return ret
    
    events = json.loads(res.text)
    for event in events:
        # get event name sometimes only one of 'name' or 'optional_label' is filled, other 'null'
        #print("event",event)
        event_name = event['name']
        if event_name is not None:
            try:
                event_name = event_name.split('_')[1]
            except IndexError:
                #raise miqtc.IfdoException("Can't parse event part from event_name: " + event_name)
                event_name = event['optional_label']
        else:
            event_name = event['optional_label']

        ret[event_name] = event['id']

    return ret


def getExpeditionIds():
    """ 
    returns dict {cruise_name: cruise_id} of all expeditions. 
    RATHER use get_expedition_id_from_label() if you look for a single
    expeditions id - much faster
    """
    ret = {}
    try:
        res = requests.get(miqtv.apis['osis_underway'] + 'expeditions', timeout=5)
    except requests.exceptions.ConnectionError:
        res = False    

    if not res:
        return ret
    
    nr_pages = json.loads(res.text)['meta']['total_pages']
    cruises = []
    for i in range(1, nr_pages + 1):
        res = requests.get(miqtv.apis['osis_underway'] + 'expeditions', params={'page':i}, timeout=5)
        cruises += json.loads(res.text)['data']

    for cruise in cruises:
        ret[cruise['name']] = cruise['id']

    return ret


def getExpeditionIdFromLabel(label:str):
    """ 
    queries osis for the expedition label and returns its id if exact match was found, 
    otherwise raise ValueError.
    """
    expeditions = getExpeditionsFromLabel(label)
    if len(expeditions) != 1:
        raise ValueError("No exact match found for label: " + label)
    else:
        return expeditions[0]['id']


def getExpeditionsFromLabel(label:str):
    """ queries osis for the expedition label and return list of matches """
    ret = {}
    try:
        res = requests.get(miqtv.apis['osis_underway'] + 'expeditions',
                           params={'filter':str({'name':label}).replace('\'','"')}, timeout=5)
    except requests.exceptions.ConnectionError:
        res = False    

    if not res:
        return ret
    
    ret = json.loads(res.text)['data']
    return ret


def getEventUrl(expedition_id:int,event_id:int):
    """ returns url to osis event """
    return miqtv.apis['osis_app'] + "expeditions/" + str(expedition_id) + "/events/" + str(event_id)


def getExpeditionUrl(expedition_id:int):
    """ returns url to osis expedition """
    return miqtv.apis['osis_app'] + "expeditions/" + str(expedition_id)


def getExpeditionIdFromUrl(osis_url:str):
    """ returns parsed expedition from url as int. Returns -1 if not successful """
    # e.g. https://osis.geomar.de/app/expeditions/359211/events/1781066
    exp_id = -1
    url_split = osis_url.split("/")
    try:
        exp_id = int(url_split[url_split.index('expeditions') + 1])
    except (ValueError, IndexError):
        pass
    return exp_id