# -*- coding: utf-8 -*-
{
    'name': 'FSM Calendar Assignee Filter',
    'summary': 'Adds Assigned To filtering and filter persistence in FSM calendar',
    'author': 'Dhara Patel',
    'category': 'Services/Field Service',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['industry_fsm'],
    'data': [
        'views/project_task.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fsm_task_calendar_assignee_filter/static/src/views/fsm_calendar_filter_persistence.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
