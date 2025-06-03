from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.test import TestCase

from ..constants import TemplateName


class TemplateNamesTest(TestCase):
    """
    Checks that template names coincide with a valid template.
    """

    def test_template_names(self):
        for template_path in TemplateName:
            try:
                get_template(template_path)
            except TemplateDoesNotExist:
                self.fail(f"Could not find a valid template at '{template_path}'")
