# -*- coding: utf-8 -*-

from plone import api
from plone.all_in_one_accessibility import _
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.schema import Choice

AIOA_SELECT_CHOICES = [
    'top_left',
    'top_center',
    'top_right',
    'middle_left',
    'middle_center',
    'middle_right',
    'bottom_left',
    'bottom_center',
    'bottom_right',
]

AIOA_SIZE_CHOICES = [
    'regular',
    'oversize',
]

TO_THE_RIGHT_CHOICES = [
    'to_the_left',
    'to_the_right',
]

TO_THE_BOTTOM_CHOICES = [
    'to_the_bottom',
    'to_the_top',
]

AIOA_ICON_SIZE_CHOICES = [
    'aioa-big-icon',
    'aioa-medium-icon',
    'aioa-default-icon',
    'aioa-small-icon',
    'aioa-extra-small-icon',
]

ICON_CHOICES = [
    (f'aioa-icon-type-{i}', f'https://www.skynettechnologies.com/sites/default/files/aioa-icon-type-{i}.svg')
    for i in range(1, 30)
]

class IAllInOneAccessibilitySetting(model.Schema):
   
    aioa_color = schema.TextLine(
        title='Hex color code',
        description='You can customize the ADA Widget color. For example: #FF5733',
        required=False,
    )
    
    enable_widget_icon_position = schema.Bool(
        title="Enable Precise widget icon positioning",
        default=False,
        required=False,
    )

    aioa_place = schema.Choice(
        title='Where would you like to place the accessibility icon on your site',
        values=AIOA_SELECT_CHOICES,
        default='bottom_right',
        required=True,
    )

    to_the_right_px = schema.Int(
        title="Right offset (PX)",
        description="Allowed range 0 - 250",
        min=0,
        max=250,
        default=20,
        required=False,
    )

    to_the_right = schema.Choice(
        title="To the right",
        values=TO_THE_RIGHT_CHOICES,
        default='to_the_left',
        required=True,
    )

    to_the_bottom_px = schema.Int(
        title="Bottom offset (PX)",
        description="Allowed range 0 - 250",
        min=0,
        max=250,
        default=20,
        required=False,
    )

    to_the_bottom = schema.Choice(
        title="To the bottom",
        values=TO_THE_BOTTOM_CHOICES,
        default='to_the_bottom',
        required=True,
    )

    aioa_size = schema.Choice(
        title="Widget Size",
        values=AIOA_SIZE_CHOICES,
        default='oversize',
        required=True,
    )
    
    aioa_icon_type = Choice(
    title="Icon Type",
    vocabulary="plone.all_in_one_accessibility.icon_vocabulary",
    default='aioa-icon-type-1',
    required=True,
    )

    enable_icon_custom_size = schema.Bool(
        title="Enable Custom Icon Size",
        default=False,
        required=False,
    )

    aioa_size_value = schema.Int(
        title="Select exact icon size (PX)",
        description="Allowed range 20 - 150",
        min=20,
        max=150,
        default=50,
        required=False,
    )

    aioa_icon_size = schema.Choice(
        title="Desktop Icon Size",
        values=AIOA_ICON_SIZE_CHOICES,
        default='aioa-default-icon',
        required=True,
    )
    
@implementer(IAllInOneAccessibilitySetting)
class AllInOneAccessibilitySetting(Item):
    # def __init__(self, id=None, **kwargs):
    #     catalog = api.portal.get_tool('portal_catalog')
    #     brains = catalog(portal_type='All in One Accessibility Setting')
    #     if brains:
    #         raise Exception('Only one "All in One Accessibility setting" object is allowed per Plone instance')
    #     super(AllInOneAccessibilitySetting, self).__init__(id, **kwargs)
    pass
    
from z3c.form.object import registerFactoryAdapter
registerFactoryAdapter(IAllInOneAccessibilitySetting, AllInOneAccessibilitySetting)





