# -*- coding: utf-8 -*-
# This file is part of lims_interface module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import formulas

from trytond import backend
from trytond.model import ModelSQL, ModelView, fields
from trytond.transaction import Transaction
from .interface import FIELD_TYPE_SQL, FIELD_TYPE_SELECTION

__all__ = ['Table', 'TableField', 'TableView']


class ModelEmulation:
    __doc__ = None
    _table = None
    __name__ = None


class Table(ModelSQL, ModelView):
    'Interface Table'
    __name__ = 'lims.interface.table'

    name = fields.Char('Name', required=True)
    fields_ = fields.One2Many('lims.interface.table.field', 'table',
        'Fields')
    views = fields.One2Many('lims.interface.table.view', 'table',
        'Views')

    def create_table(self):
        TableHandler = backend.get('TableHandler')

        model = ModelEmulation()
        model.__doc__ = self.name
        model._table = self.name

        if TableHandler.table_exist(self.name):
            TableHandler.drop_table('', self.name)

        table = TableHandler(model)

        for name, field in [
                ('create_uid', fields.Integer),
                ('write_uid', fields.Integer),
                ('create_date', fields.Timestamp),
                ('write_date', fields.Timestamp),
                ('compilation', fields.Integer),
                ('sequence', fields.Integer),
                ('notebook_line', fields.Integer),
                ]:
            sql_type = field._sql_type
            table.add_column(name, sql_type)

        for field in self.fields_:
            sql_type = FIELD_TYPE_SQL[field.type]
            table.add_column(field.name, sql_type)
        return table

    def drop_table(self):
        transaction = Transaction()
        TableHandler = backend.get('TableHandler')
        TableHandler.drop_table('', self.name, cascade=True)
        transaction.database.sequence_delete(transaction.connection,
            self.name + '_id_seq')

    @classmethod
    def delete(cls, tables):
        for table in tables:
            table.drop_table()
        super(Table, cls).delete(tables)


class TableField(ModelSQL, ModelView):
    'Interface Table Field'
    __name__ = 'lims.interface.table.field'

    table = fields.Many2One('lims.interface.table', 'Table',
        required=True, ondelete='CASCADE')
    name = fields.Char('Name', required=True)
    string = fields.Char('String', required=True)
    type = fields.Selection([(None, '')] + FIELD_TYPE_SELECTION,
        'Field Type', required=False)
    help = fields.Text('Help')
    transfer_field = fields.Boolean('Is a transfer field')
    related_line_field = fields.Many2One('ir.model.field', 'Related Field')
    related_model = fields.Many2One('ir.model', 'Related Model')
    domain = fields.Char('Domain Value')
    formula = fields.Char('On Change With Formula')
    inputs = fields.Function(fields.Char('On Change With Inputs'),
        'get_inputs')

    def get_inputs(self, name):
        if not self.formula:
            return
        parser = formulas.Parser()
        ast = parser.ast(self.formula)[1].compile()
        return (' '.join([x for x in ast.inputs])).lower()

    def get_ast(self):
        parser = formulas.Parser()
        ast = parser.ast(self.formula)[1].compile()
        return ast


class TableView(ModelSQL, ModelView):
    'Interface Table View'
    __name__ = 'lims.interface.table.view'

    table = fields.Many2One('lims.interface.table', 'Table',
        required=True, ondelete='CASCADE')
    type = fields.Char('Type')
    arch = fields.Text('Arch')
    field_names = fields.Char('Fields')
    field_childs = fields.Char('Field Childs')
