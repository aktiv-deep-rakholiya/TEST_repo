# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase
from odoo.exceptions import UserError


class TestLogNoteCustomization(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_user = cls.env.ref("base.user_admin")
        cls.internal_user = cls.env["res.users"].search(
            [('id', '!=', cls.admin_user.id)],
            limit=1
        )
        cls.partner = cls.env.user.partner_id

    def _create_log_note(self, body="<p>Original Content</p>"):
        return self.partner.with_user(self.admin_user).message_post(
            body=body,
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )

    # ---------------------------------------------------------
    # Wizard Access
    # ---------------------------------------------------------

    def test_01_admin_can_open_delete_wizard(self):
        message = self._create_log_note()
        action = message.with_user(self.admin_user).action_open_delete_reason_wizard()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "delete.reason.wizard")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["context"]["default_message_id"], message.id)

    def test_02_non_admin_cannot_open_delete_wizard(self):
        message = self._create_log_note()
        with self.assertRaises(UserError):
            message.with_user(self.internal_user).action_open_delete_reason_wizard()

    # ---------------------------------------------------------
    # Deletion
    # ---------------------------------------------------------

    def test_03_admin_can_soft_delete_message(self):
        message = self._create_log_note(body="<p>Delete Me</p>")
        wizard = self.env["delete.reason.wizard"].with_user(self.admin_user).create({
            "message_id": message.id,
            "reason": "Duplicate entry",
        })
        result = wizard.action_confirm_delete()
        self.assertEqual(result["type"], "ir.actions.client")
        message.invalidate_recordset(["body"])
        self.assertIn("deleted by an administrator", message.body.lower())

    # ---------------------------------------------------------
    # Audit Log
    # ---------------------------------------------------------

    def test_04_audit_log_created(self):
        original_body = "<p>Original Audit Content</p>"
        message = self._create_log_note(body=original_body)
        reason = "Testing Audit"
        wizard = self.env["delete.reason.wizard"].with_user(self.admin_user).create({
            "message_id": message.id,
            "reason": reason,
        })
        wizard.action_confirm_delete()
        audit = self.env["mail.message.deletion.log"].search([
            ("message_id", "=", message.id)
        ])
        self.assertTrue(audit)
        self.assertEqual(audit.deleted_by_id.id, self.admin_user.id)
        self.assertEqual(audit.reason,reason)
        # self.assertEqual(audit.original_body, original_body)
        self.assertIn("Original Audit Content", audit.original_body)
        self.assertEqual(audit.model, message.model)
        self.assertEqual(audit.res_id, message.res_id)

    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------

    def test_05_non_admin_cannot_delete(self):
        message = self._create_log_note()
        wizard = self.env["delete.reason.wizard"].with_user(self.admin_user).create({
            "message_id": message.id,
            "reason": "Should Fail",
        })
        with self.assertRaises(UserError):
            wizard.with_user(self.internal_user).action_confirm_delete()

    # ---------------------------------------------------------
    # Audit Count
    # ---------------------------------------------------------

    def test_06_single_audit_record_created(self):
        message = self._create_log_note()
        wizard = self.env["delete.reason.wizard"].with_user(self.admin_user).create({
            "message_id": message.id,
            "reason": "Audit Check",
        })
        wizard.action_confirm_delete()
        audits = self.env["mail.message.deletion.log"].search([
            ("message_id", "=", message.id)
        ])
        self.assertEqual(len(audits), 1)

    # ---------------------------------------------------------
    # Message Not Deleted Physically
    # ---------------------------------------------------------

    def test_07_message_still_exists(self):
        message = self._create_log_note()
        wizard = self.env["delete.reason.wizard"].with_user(self.admin_user).create({
            "message_id": message.id,
            "reason": "Soft Delete"
        })
        wizard.action_confirm_delete()
        existing_message = self.env["mail.message"].browse(message.id)
        self.assertTrue(existing_message.exists())
