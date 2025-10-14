# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.hr_work_entry_contract.models.hr_work_intervals import WorkIntervals
from odoo.addons.resource.models.utils import Intervals


class ResourceBookingCombination(models.Model):
    _name = "resource.booking.combination"
    _description = "Bookable resource combinations"

    active = fields.Boolean(default=True)
    booking_count = fields.Integer(
        compute="_compute_booking_count", string="Booking count"
    )
    booking_ids = fields.One2many(
        comodel_name="resource.booking",
        inverse_name="combination_id",
        string="Bookings",
    )
    forced_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Forced calendar",
        index=True,
        help="Force a specific calendar, instead of combining the resources'.",
    )
    name = fields.Char(compute="_compute_name", store=True)
    type_count = fields.Integer(compute="_compute_type_count", string="Booking types")
    type_rel_ids = fields.One2many(
        comodel_name="resource.booking.type.combination.rel",
        inverse_name="combination_id",
        string="Resource booking types",
        help="Resource booking types where this combination is available.",
    )
    resource_ids = fields.Many2many(
        string="Resources",
        comodel_name="resource.resource",
        required=True,
        help="Resources that must be free to be booked together.",
    )

    @api.depends("booking_ids")
    def _compute_booking_count(self):
        booking_data = dict(
            self.env["resource.booking"]._read_group(
                [("combination_id", "in", self.ids)], ["combination_id"], ["__count"]
            )
        )
        for combination in self:
            combination.booking_count = booking_data.get(combination, 0)

    @api.depends("resource_ids.name", "forced_calendar_id.name")
    def _compute_name(self):
        for one in self:
            data = {
                "resources": " + ".join(sorted(one.resource_ids.mapped("name"))),
                "calendar": one.forced_calendar_id.name,
            }
            if one.forced_calendar_id:
                one.name = self.env._(
                    "%(resources)s (using calendar %(calendar)s)", **data
                )
            else:
                one.name = self.env._("%(resources)s", **data)

    @api.depends("type_rel_ids")
    def _compute_type_count(self):
        booking_data = dict(
            self.env["resource.booking.type.combination.rel"]._read_group(
                [("combination_id", "in", self.ids)], ["combination_id"], ["__count"]
            )
        )
        for combination in self:
            combination.type_count = booking_data.get(combination, 0)

    @api.constrains("booking_ids", "forced_calendar_id", "resource_ids")
    def _check_bookings_scheduling(self):
        """Scheduled bookings must have no conflicts."""
        bookings = self.mapped("booking_ids")
        return bookings._check_scheduling()

    def _get_intervals(self, start_dt, end_dt, tz):
        """Get available intervals for this booking combination."""
        base = Intervals([(start_dt, end_dt, self)])
        result = Intervals([])
        # Detached compatibility with hr_holidays_public
        for combination in self.with_context(exclude_public_holidays=True):
            combination_intervals = base
            for res in combination.resource_ids:
                if not combination_intervals:
                    break  # Can't restrict more
                calendar = combination.forced_calendar_id or res.calendar_id
                # combination_intervals &= calendar._work_intervals(start_dt,
                # end_dt, res)
                combination_intervals_in_tz = calendar._work_intervals_batch(
                    start_dt, end_dt, res
                )[res.id]
                # Convert to the specified time zone if needed
                # to display the intervals correctly in the same time zone.
                if calendar.tz != tz.zone:
                    new_intervals = []
                    for interval in combination_intervals_in_tz:
                        start = interval[0].astimezone(tz)
                        end = interval[1].astimezone(tz)
                        new_intervals.append((start, end, interval[2]))
                    combination_intervals_in_tz = WorkIntervals(new_intervals)
                combination_intervals &= combination_intervals_in_tz
            result |= combination_intervals
        return result

    def action_open_bookings(self):
        return {
            "domain": [("combination_id", "in", self.ids)],
            "name": self.env._("Bookings"),
            "res_model": "resource.booking",
            "type": "ir.actions.act_window",
            "view_mode": "calendar,list,form",
            "context": {"default_combination_id": self.id},
        }

    def action_open_resource_booking_types(self):
        return {
            "context": self.env.context,
            "domain": [("combination_rel_ids.combination_id", "in", self.ids)],
            "name": self.env._("Booking types"),
            "res_model": "resource.booking.type",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
        }
