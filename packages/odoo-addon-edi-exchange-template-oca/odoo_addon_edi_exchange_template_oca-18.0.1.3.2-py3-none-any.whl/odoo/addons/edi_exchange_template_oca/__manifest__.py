# Copyright 2020 ACSONE
# Copyright 2022 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "EDI Exchange Template",
    "summary": """Allows definition of exchanges via templates.""",
    "version": "18.0.1.3.2",
    "development_status": "Beta",
    "license": "LGPL-3",
    "author": "ACSONE,Camptocamp,Odoo Community Association (OCA)",
    "maintainers": ["simahawk"],
    "website": "https://github.com/OCA/edi-framework",
    "depends": ["edi_core_oca"],
    "data": [
        "security/ir_model_access.xml",
        "views/edi_exchange_template_output_views.xml",
        "views/edi_exchange_type_views.xml",
    ],
}
