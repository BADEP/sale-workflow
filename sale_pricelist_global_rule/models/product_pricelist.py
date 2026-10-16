from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    applied_on = fields.Selection(
        selection_add=[
            ("3_1_global_product_template", "Global - Product template"),
            ("3_2_global_product_category", "Global - Product category"),
        ],
        ondelete={
            "3_1_global_product_template": "set 3_global",
            "3_2_global_product_category": "set 3_global",
        },
    )
    global_product_tmpl_id = fields.Many2one(
        "product.template",
        "Global Product",
        ondelete="cascade",
        check_company=True,
    )
    global_categ_id = fields.Many2one(
        "product.category",
        "Product Category",
        ondelete="cascade",
    )

    @api.constrains(
        "product_id",
        "product_tmpl_id",
        "categ_id",
        "global_product_tmpl_id",
        "global_categ_id",
    )
    def _check_product_consistency(self):
        res = super()._check_product_consistency()
        for item in self:
            if (
                item.applied_on == "3_2_global_product_category"
                and not item.global_categ_id
            ):
                raise ValidationError(
                    self.env._(
                        "Please specify the category "
                        "for which this global rule should be applied"
                    )
                )
            elif (
                item.applied_on == "3_1_global_product_template"
                and not item.global_product_tmpl_id
            ):
                raise ValidationError(
                    self.env._(
                        "Please specify the product "
                        "for which this global rule should be applied"
                    )
                )
        return res

    @api.depends("global_product_tmpl_id", "global_categ_id")
    def _compute_applied_on(self):
        res = super()._compute_applied_on()
        for item in self:
            if item.categ_id or item.product_tmpl_id:
                continue
            if item.global_categ_id:
                item.applied_on = "3_2_global_product_category"
            elif item.global_product_tmpl_id:
                item.applied_on = "3_1_global_product_template"
        return res

    @api.depends("global_product_tmpl_id", "global_categ_id")
    def _compute_name(self):
        res = super()._compute_name()
        for item in self:
            if (
                item.global_categ_id
                and item.applied_on == "3_2_global_product_category"
            ):
                item.name = self.env._(
                    "Global category: %s", item.global_categ_id.display_name
                )
            elif (
                item.global_product_tmpl_id
                and item.applied_on == "3_1_global_product_template"
            ):
                item.name = self.env._(
                    "Global product: %s", item.global_product_tmpl_id.display_name
                )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get("applied_on", False):
                # Ensure item consistency for later searches.
                applied_on = values["applied_on"]
                if applied_on == "3_2_global_product_category":
                    values.update(
                        {
                            "product_id": None,
                            "product_tmpl_id": None,
                            "categ_id": None,
                            "global_product_tmpl_id": None,
                        }
                    )
                elif applied_on == "3_1_global_product_template":
                    values.update(
                        {
                            "product_id": None,
                            "product_tmpl_id": None,
                            "categ_id": None,
                            "global_categ_id": None,
                        }
                    )
        return super().create(vals_list)

    def write(self, values):
        if values.get("applied_on", False):
            # Ensure item consistency for later searches.
            applied_on = values["applied_on"]
            if applied_on == "3_2_global_product_category":
                values.update(
                    {
                        "product_id": None,
                        "product_tmpl_id": None,
                        "categ_id": None,
                        "global_product_tmpl_id": None,
                    }
                )
            elif applied_on == "3_1_global_product_template":
                values.update(
                    {
                        "product_id": None,
                        "product_tmpl_id": None,
                        "categ_id": None,
                        "global_categ_id": None,
                    }
                )
        return super().write(values)

    def _is_applicable_for(self, product, quantity, *, uom=None, **kwargs):
        """Check whether the current rule is valid
        for the given sale order and cummulated quantity.
        :param product_template: browse_record(product.template)
        :param qty_data:
            dict{
                by_categ: dict{record<product.categ>: qty, ...},
                by_template: dict{record<product.template>: qty, ...}
            }
        :returns: Whether rules is valid or not
        :rtype: bool
        """
        self.ensure_one()
        qty_data = self.env.context.get(
            "pricelist_global_cummulative_quantity", {"by_template": {}, "by_categ": {}}
        )
        if self.applied_on not in [
            "3_1_global_product_template",
            "3_2_global_product_category",
        ]:
            return super()._is_applicable_for(product, quantity, uom=uom, **kwargs)
        is_applicable = True
        if self.applied_on == "3_1_global_product_template":
            total_qty = qty_data["by_template"].get(product.product_tmpl_id, 0.0)
            if (
                self.min_quantity
                and total_qty < self.min_quantity
                or self.global_product_tmpl_id != product.product_tmpl_id
            ):
                is_applicable = False
        elif self.applied_on == "3_2_global_product_category":
            total_qty = qty_data["by_categ"].get(product.categ_id, 0.0)
            if (
                self.min_quantity
                and total_qty < self.min_quantity
                or not product.categ_id.parent_path.startswith(
                    self.global_categ_id.parent_path
                )
            ):
                is_applicable = False
        return is_applicable
