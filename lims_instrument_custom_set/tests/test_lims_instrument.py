# This file is part of lims_instrument_custom_set module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class LimsTestCase(ModuleTestCase):
    'Test lims_instrument_custom_set module'
    module = 'lims_instrument_custom_set'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            LimsTestCase))
    return suite
