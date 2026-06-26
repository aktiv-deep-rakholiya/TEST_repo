from odoo import fields, models


class MailMessageDeletionLog(models.Model):
    _name = "mail.message.deletion.log"
    _description = "Deleted Message Audit"
    _order = "deleted_on desc"

    message_id = fields.Many2one("mail.message", readonly=True, ondelete="set null")
    deleted_by_id = fields.Many2one("res.users", string="Deleted By", required=True, readonly=True)
    deleted_on = fields.Datetime(required=True, readonly=True)
    reason = fields.Text(required=True, readonly=True)
    original_body = fields.Html(readonly=True)
    model = fields.Char(readonly=True)
    res_id = fields.Integer(readonly=True)
