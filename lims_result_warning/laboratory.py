# This file is part of lims_result_warning module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import PoolMeta

__all__ = ['NotebookRule']


class NotebookRule(metaclass=PoolMeta):
    __name__ = 'lims.rule'

    @classmethod
    def _target_fields(cls):
        field_list = super(NotebookRule, cls)._target_fields()
        field_list.append('result_warning')
        return field_list
