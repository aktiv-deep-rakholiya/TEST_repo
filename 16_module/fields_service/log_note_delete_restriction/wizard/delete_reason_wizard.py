from odoo import fields, models, _
from odoo.exceptions import UserError


class DeleteReasonWizard(models.TransientModel):
    _name = "delete.reason.wizard"
    _description = "Delete Message Reason"

    message_id = fields.Many2one("mail.message", required=True)
    reason = fields.Text(required=True, string="Reason")

    def action_confirm_delete(self):
        self.ensure_one()

        if not self.env.user.has_group("base.group_system"):
            raise UserError(_("Only administrators can delete messages."))

        message = self.message_id.sudo()

        if not message.exists():
            raise UserError(_("Message no longer exists."))

        self.env["mail.message.deletion.log"].create({
            "message_id": message.id,
            "deleted_by_id": self.env.user.id,
            "deleted_on": fields.Datetime.now(),
            "reason": self.reason,
            "original_body": message.body,
            "model": message.model,
            "res_id": message.res_id,
        })

        message.write({
            "body": _("This message was deleted by an administrator.")
        })

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
