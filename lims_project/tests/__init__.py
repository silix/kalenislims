# This file is part of lims_project module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

try:
    from trytond.modules.lims_project.tests.test_lims_project import suite
except ImportError:
    from .test_lims_project import suite

__all__ = ['suite']
