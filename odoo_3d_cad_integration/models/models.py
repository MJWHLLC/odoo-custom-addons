from odoo import models, fields

class CADViewer(models.Model):
    _name = 'cad.viewer'
    _description = '3D CAD Viewer'

    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='3D CAD URL', required=True, help='URL to the 3D CAD viewer interface')
