# Copyright 2014 Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
# Copyright 2015-2020 Tecnativa - Pedro M. Baeza
# Copyright 2015 Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2023 glueckkanja AG - CRogos
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_update_prices(self):
        # Removed from sale in 20.0, kept here as this module's button relies on it
        self.ensure_one()
        self._recompute_prices()
        if self.pricelist_id:
            message = self.env._(
                "Product prices have been recomputed according to pricelist %s.",
                self.pricelist_id._get_html_link(),
            )
        else:
            message = self.env._("Product prices have been recomputed.")
        self.message_post(body=message)

    def action_update_names(self):
        lines = self.mapped("order_line")
        lines._compute_name()
        return True
