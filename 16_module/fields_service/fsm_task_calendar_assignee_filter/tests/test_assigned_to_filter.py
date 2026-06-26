# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.addons.industry_fsm.tests.common import TestIndustryFsmCommon


@tagged("post_install", "-at_install")
class TestAssignedToFilter(TestIndustryFsmCommon):
    """Tests for the FSM calendar 'Assigned To' filter."""

    @classmethod
    def _create_task(cls, name, user_ids=None):
        return cls.env["project.task"].create({
            "name": name,
            "project_id": cls.fsm_project.id,
            "user_ids": [(6, 0, user_ids or [])],
            "partner_id": cls.partner.id,
        })

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_fitter_1 = cls.george_user
        cls.user_fitter_2 = cls.marcel_user

        cls.task_fitter_1 = cls._create_task(
            "Task for Fitter 1",
            [cls.user_fitter_1.id],
        )

        cls.task_fitter_2 = cls._create_task(
            "Task for Fitter 2",
            [cls.user_fitter_2.id],
        )

        cls.task_both_fitters = cls._create_task(
            "Task for Both Fitters",
            [cls.user_fitter_1.id, cls.user_fitter_2.id],
        )

        cls.task_unassigned = cls._create_task(
            "Unassigned Task",
        )

    def test_01_calendar_view_has_assigned_to_filter(self):
        """Verify the calendar view exposes the Assigned To filter."""

        calendar_view = self.env.ref("industry_fsm.project_task_view_calendar_fsm")

        arch = self.env["project.task"].get_view(
            view_id=calendar_view.id,
            view_type="calendar",
        )["arch"]

        self.assertIn(
            'name="user_ids"',
            arch,
            "user_ids field should be present in the calendar view",
        )
        self.assertIn(
            'filters="1"',
            arch,
            "user_ids field should be configured as a filter",
        )

    def test_02_filter_single_user(self):
        """Tasks assigned to the selected fitter should be returned."""

        tasks = self.env["project.task"].search([
            ("is_fsm", "=", True),
            ("project_id", "=", self.fsm_project.id),
            ("user_ids", "in", [self.user_fitter_1.id]),
        ])

        self.assertIn(
            self.task_fitter_1,
            tasks,
            "Task assigned to fitter 1 should be returned",
        )
        self.assertIn(
            self.task_both_fitters,
            tasks,
            "Task assigned to both fitters should be returned",
        )
        self.assertNotIn(
            self.task_fitter_2,
            tasks,
            "Task assigned only to fitter 2 should not be returned",
        )
        self.assertNotIn(
            self.task_unassigned,
            tasks,
            "Unassigned task should not be returned",
        )

    def test_03_filter_multiple_users(self):
        """Tasks assigned to any selected fitter should be returned."""

        tasks = self.env["project.task"].search([
            ("is_fsm", "=", True),
            ("project_id", "=", self.fsm_project.id),
            ("user_ids", "in", [
                self.user_fitter_1.id,
                self.user_fitter_2.id,
            ]),
        ])

        self.assertIn(self.task_fitter_1, tasks)
        self.assertIn(self.task_fitter_2, tasks)
        self.assertIn(self.task_both_fitters, tasks)
        self.assertNotIn(self.task_unassigned, tasks)

    def test_04_no_filter_shows_all_tasks(self):
        """Without a user filter, all FSM tasks should be returned."""

        tasks = self.env["project.task"].search([
            ("is_fsm", "=", True),
            ("project_id", "=", self.fsm_project.id),
        ])

        self.assertIn(self.task_fitter_1, tasks)
        self.assertIn(self.task_fitter_2, tasks)
        self.assertIn(self.task_both_fitters, tasks)
        self.assertIn(self.task_unassigned, tasks)
