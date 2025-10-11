"""Custom WTForms widgets for govuk-flask-admin."""
from govuk_frontend_wtf.gov_form_base import GovFormBase
from wtforms.widgets.core import Select


class GovSelectWithSearch(GovFormBase, Select):
    """
    GOV.UK Select widget enhanced with search functionality using Choices.js.

    Based on the select-with-search component from govuk_publishing_components:
    https://github.com/alphagov/govuk_publishing_components/tree/main/app/views/govuk_publishing_components/components/select_with_search

    Uses Choices.js for progressive enhancement:
    https://github.com/Choices-js/Choices

    Renders a <select> element with data-module="select-with-search"
    which is progressively enhanced by Choices.js for search and multi-select.

    This widget supports both single-select and multi-select modes.
    Unlike the standard GovSelect, this widget allows multiple selection
    which is acceptable when combined with search functionality.

    The Python widget is custom implementation for Flask-Admin/WTForms,
    while the JavaScript/CSS are adapted from govuk_publishing_components.
    """

    template = "select-with-search.html"

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)

        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True

        kwargs["items"] = []

        # Construct select box choices
        for val, label, selected, render_kw in field.iter_choices():
            item = {"text": label, "value": val, "selected": selected}
            kwargs["items"].append(item)

        # Pass multiple flag to template
        kwargs["multiple"] = self.multiple

        return super().__call__(field, **kwargs)

    def map_gov_params(self, field, **kwargs):
        # Save items list before parent deletes it from kwargs
        select_items = kwargs.get("items", [])
        multiple = kwargs.get("multiple", False)

        params = super().map_gov_params(field, **kwargs)

        # Use 'select_items' to avoid collision with dict.items() method
        params["select_items"] = select_items
        params["multiple"] = multiple

        return params
