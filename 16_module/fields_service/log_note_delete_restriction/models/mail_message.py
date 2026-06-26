# -*- coding: utf-8 -*-

from markupsafe import Markup
from odoo import models, fields, _
from odoo.exceptions import UserError


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def action_open_delete_reason_wizard(self):
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise UserError("You are not allowed to delete messages.")

        return {
            "type": "ir.actions.act_window",
            "name": _("Delete Message"),
            "res_model": "delete.reason.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_message_id": self.id,
            },
        }
