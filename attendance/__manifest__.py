# -*- coding: utf-8 -*-
{
    'name': "evlattendance",

    'summary': """
        Ergo Ventures Pvt. Ltd.""",

    'description': """
        Ergo Ventures Pvt. Ltd.

    """,
    'author': "Hisham Ahmed",
    'website': "https://www.ergo-ventures.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_attendance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/actions.xml',
        'security/ir.model.access.csv',
        'views/res_config_cron_setting.xml',
        'views/device_config.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    # 'qweb': ['static/one.xml'],

}