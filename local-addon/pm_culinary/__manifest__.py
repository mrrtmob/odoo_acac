# -*- coding: utf-8 -*-
{
    'name': "Pathmazing Culinary",
    'sequence': 2,
    'summary': "Culinary App",
    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product',
        'openeducat_core',
        'mail',
        'pm_approval',
        'uom',
        'purchase',
    ],

    # always loaded
    'data': [
        'wizards/recipe_detail_wizard_views.xml',
        'wizards/recipe_schedule_wizard_views.xml',
        'report/pm_recipe_reports.xml',
        'report/pm_recipe_detail_templates.xml',
        'report/pm_recipe_schedule_templates.xml',
        'security/culinary_security.xml',
        'security/ir.model.access.csv',
        'views/pm_brand_views.xml',
        'views/pm_ingredient_category_views.xml',
        'views/pm_ingredient_origin_views.xml',
        'views/pm_ingredient_views.xml',
        'views/pm_menu_line_views.xml',
        'views/pm_menu_views.xml',
        'views/pm_non_food_product_views.xml',
        'views/pm_nutrition_views.xml',
        'views/pm_product_uom_views.xml',
        'views/pm_purchase_order_line_views.xml',
        'views/pm_recipe_line_views.xml',
        'views/pm_schedule_menu_views.xml',
        'views/pm_schedule_views.xml',
        'views/pm_supplier_industry_views.xml',
        'views/product_category_views.xml',
        'views/product_supplierinfo_views.xml',
        'views/res_partner_views.xml',
        'views/pm_recipe_view.xml',
        'views/pm_dashboard.xml',
        'views/pm_culinary_menus.xml',
        'views/purchase_menus.xml',
        'views/templates.xml',
        'data/culinary_portal_menu.xml',
        'data/cron.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
