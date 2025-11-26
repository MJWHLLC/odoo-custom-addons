# -*- coding: utf-8 -*-
{
    'name': '3D CAD Integration',
    'version': '19.0.1.0.0',
    'summary': 'Integrate 3D CAD viewer compatible with multiple platforms including mobile, desktop, VR, and MR',
    'description': """
3D CAD Integration
==================
This module provides integration with a 3D computer-assisted design system accessible from Android, iOS, Windows, Mac, VR, and MR platforms.

Features:
---------
* Multi-platform 3D CAD viewer
* Compatible with Android, iOS, Windows, Mac
* VR and MR support
* Web-based interface
    """,
    'author': 'MJ Wilkerson Holdings LLC',
    'website': 'https://mj-wilkerson-holdings-llc.odoo.com',
    'category': 'Tools',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'views/3d_cad_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
