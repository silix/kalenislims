# -*- coding: utf-8 -*-
# This file is part of lims_digital_sign module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Configuration', 'Cron']


class Configuration(metaclass=PoolMeta):
    __name__ = 'lims.configuration'

    mail_ack_report_subject = fields.Char('Email subject of Acknowledgment of'
        ' results report',
        help='In the text will be added suffix with the results report number')
    mail_ack_report_body = fields.Text('Email body of Acknowledgment of'
        ' results report',
        help='<SAMPLES> will be replaced by the list of sample\'s labels')


class Cron(metaclass=PoolMeta):
    __name__ = 'ir.cron'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.method.selection.extend([
                ('lims.results_report|cron_digital_signs',
                    "Cron Lims Digital Sign"),
                ])
