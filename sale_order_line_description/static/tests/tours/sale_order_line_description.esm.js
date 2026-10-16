/* Copyright 2026 Moduon
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {registry} from "@web/core/registry";
import {stepUtils} from "@web_tour/tour_utils";

registry.category("web_tour.tours").add("sale_order_line_description_manual_edit", {
  steps: () => [
    {
      content: "Check the product name is shown on its own line",
      trigger: '.o_field_widget[name="label"] .o_has_product:text("Test product")',
    },
    {
      content:
        "Check the product name is not prepended to the description and open the line editor",
      trigger:
        '.o_field_widget[name="label"] .fst-italic:text("Sale description for test product")',
      run: "click",
    },
    {
      content: "Edit the sale order line description",
      trigger: '.o_selected_row .o_field_widget[name="label"] textarea',
      run(helpers) {
        // Append to the description line (typing on the first line, which
        // holds the product name, would search for another product)
        return helpers.fill(" test");
      },
    },
    {
      content: "Leave the description to commit the change",
      trigger: '.o_selected_row .o_field_widget[name="label"] textarea',
      run: "press Tab",
    },
    {
      content: "Wait for the order to be marked as modified",
      trigger: ".o_form_dirty",
    },
    ...stepUtils.saveForm(),
  ],
});
