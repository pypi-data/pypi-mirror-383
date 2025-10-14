# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Line Chained Move",
    "summary": """
        This module adds a field on sale order line to get all related move lines""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/sale-workflow",
    "development_status": "Production/Stable",
    "depends": ["sale_stock"],
    "data": ["views/stock_rule_views.xml"],
    "post_init_hook": "post_init_hook",
}
