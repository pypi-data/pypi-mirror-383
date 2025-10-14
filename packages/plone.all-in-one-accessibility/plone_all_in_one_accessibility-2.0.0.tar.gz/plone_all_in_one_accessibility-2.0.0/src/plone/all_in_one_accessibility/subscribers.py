# subscribers.py
import json
import requests
from urllib.parse import urlparse
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent, IObjectAddedEvent
from zope.globalrequest import getRequest
from plone.all_in_one_accessibility.content.all_in_one_accessibility_setting import (
    IAllInOneAccessibilitySetting
)
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from plone import api
from zope.component import adapter, getUtility
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from plone.dexterity.interfaces import IDexterityFTI
from plone.all_in_one_accessibility.content.all_in_one_accessibility_setting import IAllInOneAccessibilitySetting
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


API_URL = "https://ada.skynettechnologies.us/api/widget-setting-update-platform"  

@adapter(IAllInOneAccessibilitySetting, IObjectAddedEvent)
def send_to_external_api_on_add(obj, event):
    _send_data(obj)

@adapter(IAllInOneAccessibilitySetting, IObjectModifiedEvent)
def send_to_external_api_on_edit(obj, event):
    _send_data(obj)

def _send_data(obj):
    # Try to get the Plone request
    request = getattr(obj, "REQUEST", None)
    if request is None:
        try:
            request = getRequest()
        except ImportError:
            request = None

    if request is None:
        return
    
    # Extract domain (scheme + hostname) from actual URL
    actual_url = request.get("ACTUAL_URL", "") or request.get("URL", "")
    parsed = urlparse(actual_url)
    domain_url = f"{parsed.scheme}://{parsed.hostname}" if parsed.hostname else ""

    data = {
        "u": domain_url,
        "widget_color_code": obj.aioa_color or "",
        "is_widget_custom_position": int(bool(obj.enable_widget_icon_position)),
        "is_widget_custom_size": int(bool(obj.enable_icon_custom_size)),
    }

    # Position settings
    if not obj.enable_widget_icon_position:
        data.update({
            "widget_position_top": 0,
            "widget_position_right": 0,
            "widget_position_bottom": 0,
            "widget_position_left": 0,
            "widget_position": obj.aioa_place or "",
        })
    else:
        pos = {
            "widget_position_top": 0,
            "widget_position_right": 0,
            "widget_position_bottom": 0,
            "widget_position_left": 0,
        }

        if obj.to_the_right == "to_the_left":
            pos["widget_position_left"] = obj.to_the_right_px or 0
        elif obj.to_the_right == "to_the_right":
            pos["widget_position_right"] = obj.to_the_right_px or 0

        if obj.to_the_bottom == "to_the_bottom":
            pos["widget_position_bottom"] = obj.to_the_bottom_px or 0
        elif obj.to_the_bottom == "to_the_top":
            pos["widget_position_top"] = obj.to_the_bottom_px or 0

        data.update(pos)
        data["widget_position"] = ""  # ignore aioa_place when custom position is used

    # Icon size settings
    if not obj.enable_icon_custom_size:
        data.update({
            "widget_icon_size": obj.aioa_icon_size or "",
            "widget_icon_size_custom": 0,
        })
    else:
        data.update({
            "widget_icon_size": "",
            "widget_icon_size_custom": obj.aioa_size_value or 0,
        })

    # Widget size: 1 = oversize, 0 = regular
    data["widget_size"] = 1 if obj.aioa_size == "oversize" else 0

    # Icon type
    data["widget_icon_type"] = obj.aioa_icon_type or ""

    files=[
        
        ]
    headers = {}
    try:
        response = requests.post(API_URL, headers=headers, data=data, files=files)
        response.raise_for_status()
    except requests.RequestException as e:
        error_content = None
        if 'response' in locals() and response is not None:
            try:
                error_content = response.json()  # Try parsing JSON error
            except Exception:
                error_content = response.text  # Fallback to raw text
        else:
            error_content = str(e)  # If no response at all (e.g., network error)


@adapter(IAllInOneAccessibilitySetting, IObjectAddedEvent)
def disable_add_after_creation(obj, event):
    fti = getUtility(IDexterityFTI, name='All in One Accessibility Setting')
    if fti.global_allow:
        fti.global_allow = False
        fti._p_changed = True


@adapter(IAllInOneAccessibilitySetting, IObjectRemovedEvent)
def enable_add_after_deletion(obj, event):
    fti = getUtility(IDexterityFTI, name='All in One Accessibility Setting')
    if not fti.global_allow:
        fti.global_allow = True
        fti._p_changed = True





