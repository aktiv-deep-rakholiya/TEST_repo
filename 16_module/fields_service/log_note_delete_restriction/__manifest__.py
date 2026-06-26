# -*- coding: utf-8 -*-
{
    'name': 'Log Note Delete Restriction',
    "version": "19.0.1.0.0",
    'category': 'Discuss',
    'summary': "Restrict log note deletion and maintain audit trail",
    'author': 'Dhara Patel',
    'license': 'LGPL-3',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/delete_reason_wizard.xml',
        "views/mail_message_deletion_log_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'log_note_delete_restriction/static/src/js/hide_delete_action.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
