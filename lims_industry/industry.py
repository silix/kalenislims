# This file is part of lims_industry module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import ModelSQL, ModelView, fields, Unique
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['Plant', 'EquipmentType', 'Brand', 'ComponentType',
    'EquipmentTemplate', 'EquipmentTemplateComponentType', 'Equipment',
    'Component', 'ComercialProductBrand', 'ComercialProduct']


class Plant(ModelSQL, ModelView):
    'Plant'
    __name__ = 'lims.plant'

    party = fields.Many2One('party.party', 'Party', required=True,
        ondelete='CASCADE', select=True,
        states={'readonly': Eval('id', 0) > 0}, depends=['id'])
    name = fields.Char('Name', required=True)
    street = fields.Char('Street', required=True)
    zip = fields.Char('Zip', required=True)
    city = fields.Char('City', required=True)
    subdivision = fields.Many2One('country.subdivision',
        'Subdivision', required=True, domain=[
            ('country', '=', Eval('country', -1)),
            ('parent', '=', None),
            ],
        depends=['country'])
    country = fields.Many2One('country.country', 'Country',
        required=True)
    equipments = fields.One2Many('lims.equipment', 'plant',
        'Equipments')
    contacts = fields.One2Many('party.address', 'plant',
        'Contacts', domain=[('party', '=', Eval('party'))],
        depends=['party'])
    invoice_party = fields.Many2One('party.party', 'Invoice Party')
    latitude = fields.Numeric('Latitude', digits=(3, 14))
    longitude = fields.Numeric('Longitude', digits=(4, 14))

    @classmethod
    def __setup__(cls):
        super(Plant, cls).__setup__()
        cls._order.insert(0, ('party', 'ASC'))
        cls._order.insert(1, ('name', 'ASC'))
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_unique', Unique(t, t.party, t.name),
                'lims_industry.msg_plant_name_unique'),
            ]

    @staticmethod
    def default_country():
        Company = Pool().get('company.company')
        company_id = Transaction().context.get('company')
        if company_id:
            address = Company(company_id).party.address_get()
            if address and address.country:
                return address.country.id

    @classmethod
    def copy(cls, plants, default=None):
        if default is None:
            default = {}
        default = default.copy()

        new_plants = []
        for plant in plants:
            default['name'] = plant.name + ' (copy)'
            default['equipments'] = None
            new_plant, = super(Plant, cls).copy([plant], default)
            new_plants.append(new_plant)
        return new_plants


class EquipmentType(ModelSQL, ModelView):
    'Equipment Type'
    __name__ = 'lims.equipment.type'

    name = fields.Char('Name', required=True)


class Brand(ModelSQL, ModelView):
    'Brand'
    __name__ = 'lims.brand'

    name = fields.Char('Name', required=True)


class ComponentType(ModelSQL, ModelView):
    'Component Type'
    __name__ = 'lims.component.type'

    name = fields.Char('Name', required=True)
    product_type = fields.Many2One('lims.product.type', 'Product type',
        required=True)


class EquipmentTemplate(ModelSQL, ModelView):
    'Equipment Template'
    __name__ = 'lims.equipment.template'

    type = fields.Many2One('lims.equipment.type', 'Type', required=True)
    brand = fields.Many2One('lims.brand', 'Brand', required=True)
    model = fields.Char('Model')
    power = fields.Char('Power')
    component_types = fields.Many2Many(
        'lims.equipment.template-component.type',
        'template', 'type', 'Component types')

    @classmethod
    def __setup__(cls):
        super(EquipmentTemplate, cls).__setup__()
        cls._order.insert(0, ('type', 'ASC'))
        cls._order.insert(1, ('brand', 'ASC'))
        cls._order.insert(2, ('model', 'ASC'))

    def get_rec_name(self, name):
        res = '%s - %s' % (self.type.rec_name, self.brand.rec_name)
        if self.model:
            res += ' - ' + self.model
        return res

    @classmethod
    def search_rec_name(cls, name, clause):
        return ['OR',
            ('type.name',) + tuple(clause[1:]),
            ('brand.name',) + tuple(clause[1:]),
            ('model',) + tuple(clause[1:]),
            ]


class EquipmentTemplateComponentType(ModelSQL):
    'Equipment Template - Component Type'
    __name__ = 'lims.equipment.template-component.type'
    _table = 'lims_equipment_template_component_type'

    template = fields.Many2One('lims.equipment.template', 'Template',
        required=True, ondelete='CASCADE', select=True)
    type = fields.Many2One('lims.component.type', 'Type',
        required=True, ondelete='CASCADE', select=True)


class Equipment(ModelSQL, ModelView):
    'Equipment'
    __name__ = 'lims.equipment'

    template = fields.Many2One('lims.equipment.template', 'Template',
        required=True)
    name = fields.Char('Name', required=True)
    brand = fields.Function(fields.Many2One('lims.brand', 'Brand'),
        'get_brand', searcher='search_brand')
    model = fields.Char('Model', required=True)
    power = fields.Char('Power')
    serial_number = fields.Char('Serial number')
    internal_id = fields.Char('Internal ID Code')
    latitude = fields.Numeric('Latitude', digits=(3, 14))
    longitude = fields.Numeric('Longitude', digits=(4, 14))
    plant = fields.Many2One('lims.plant', 'Plant',
        required=True, select=True)
    components = fields.One2Many('lims.component', 'equipment',
        'Components')
    year_manufacturing = fields.Integer('Year of manufacturing')
    internal_location = fields.Char('Internal location')
    contacts = fields.One2Many('party.address', 'equipment',
        'Contacts', domain=[('party', '=', Eval('party'))],
        context={'plant': Eval('plant')},
        depends=['party', 'plant'])
    party = fields.Function(fields.Many2One('party.party', 'Party'),
        'get_party', searcher='search_party')
    missing_data = fields.Boolean('Missing data')

    @classmethod
    def __setup__(cls):
        super(Equipment, cls).__setup__()
        cls._order.insert(0, ('template', 'ASC'))
        cls._order.insert(1, ('name', 'ASC'))
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_unique', Unique(t, t.plant, t.name),
                'lims_industry.msg_equipment_name_unique'),
            ]

    @classmethod
    def create(cls, vlist):
        TaskTemplate = Pool().get('lims.administrative.task.template')
        equipments = super(Equipment, cls).create(vlist)
        TaskTemplate.create_tasks('equipment_missing_data',
            cls._for_task_missing_data(equipments))
        return equipments

    @classmethod
    def _for_task_missing_data(cls, equipments):
        AdministrativeTask = Pool().get('lims.administrative.task')
        res = []
        for equipment in equipments:
            if not equipment.missing_data:
                continue
            if AdministrativeTask.search([
                    ('type', '=', 'equipment_missing_data'),
                    ('origin', '=', '%s,%s' % (cls.__name__, equipment.id)),
                    ('state', 'not in', ('done', 'discarded')),
                    ]):
                continue
            res.append(equipment)
        return res

    @fields.depends('plant', '_parent_plant.party')
    def on_change_with_party(self, name=None):
        return self.get_party([self], name)[self.id]

    @classmethod
    def get_party(cls, equipments, name):
        result = {}
        for e in equipments:
            result[e.id] = e.plant and e.plant.party.id or None
        return result

    @classmethod
    def search_party(cls, name, clause):
        return [('plant.party',) + tuple(clause[1:])]

    @fields.depends('template', '_parent_template.brand')
    def on_change_with_brand(self, name=None):
        return self.get_brand([self], name)[self.id]

    @classmethod
    def get_brand(cls, equipments, name):
        result = {}
        for e in equipments:
            result[e.id] = e.template and e.template.brand.id or None
        return result

    @classmethod
    def search_brand(cls, name, clause):
        return [('template.brand',) + tuple(clause[1:])]

    @fields.depends('template')
    def on_change_template(self):
        pool = Pool()
        Component = pool.get('lims.component')

        model = None
        power = None
        components = []
        if self.template:
            model = self.template.model
            power = self.template.power
            for type in self.template.component_types:
                value = Component(**Component.default_get(
                    list(Component._fields.keys()), with_rec_name=False))
                value.type = type.id
                components.append(value)
        self.model = model
        self.power = power
        self.components = components

    @classmethod
    def copy(cls, equipments, default=None):
        if default is None:
            default = {}
        default = default.copy()

        new_equipments = []
        for equipment in equipments:
            default['name'] = equipment.name + ' (copy)'
            new_equipment, = super(Equipment, cls).copy([equipment], default)
            new_equipments.append(new_equipment)
        return new_equipments


class Component(ModelSQL, ModelView):
    'Component'
    __name__ = 'lims.component'

    equipment = fields.Many2One('lims.equipment', 'Equipment',
        required=True, ondelete='CASCADE', select=True)
    type = fields.Many2One('lims.component.type', 'Type',
        required=True)
    product_type = fields.Function(fields.Many2One('lims.product.type',
        'Product type'), 'get_product_type')
    comercial_product = fields.Many2One('lims.comercial.product',
        'Comercial product')
    capacity = fields.Char('Capacity (lts)')
    serial_number = fields.Char('Serial number')
    model = fields.Char('Model')
    power = fields.Char('Power')
    brand = fields.Many2One('lims.brand', 'Brand')
    internal_id = fields.Char('Internal ID Code')
    customer_description = fields.Char('Customer description')
    year_manufacturing = fields.Integer('Year of manufacturing')
    plant = fields.Function(fields.Many2One('lims.plant', 'Plant'),
        'get_plant', searcher='search_plant')
    party = fields.Function(fields.Many2One('party.party', 'Party'),
        'get_party', searcher='search_party')
    missing_data = fields.Boolean('Missing data')

    @classmethod
    def __setup__(cls):
        super(Component, cls).__setup__()
        cls._order.insert(0, ('equipment', 'ASC'))
        cls._order.insert(1, ('type', 'ASC'))
        t = cls.__table__()
        cls._sql_constraints = [
            ('type_unique', Unique(t, t.equipment, t.type),
                'lims_industry.msg_component_type_unique'),
            ]

    @classmethod
    def create(cls, vlist):
        TaskTemplate = Pool().get('lims.administrative.task.template')
        components = super(Component, cls).create(vlist)
        TaskTemplate.create_tasks('component_missing_data',
            cls._for_task_missing_data(components))
        return components

    @classmethod
    def _for_task_missing_data(cls, components):
        AdministrativeTask = Pool().get('lims.administrative.task')
        res = []
        for component in components:
            if not component.missing_data:
                continue
            if AdministrativeTask.search([
                    ('type', '=', 'component_missing_data'),
                    ('origin', '=', '%s,%s' % (cls.__name__, component.id)),
                    ('state', 'not in', ('done', 'discarded')),
                    ]):
                continue
            res.append(component)
        return res

    def get_rec_name(self, name):
        res = self.type.rec_name
        if self.brand:
            res += ' - ' + self.brand.rec_name
        if self.model:
            res += ' - ' + self.model
        return res

    @classmethod
    def get_plant(cls, component, name):
        result = {}
        for c in component:
            result[c.id] = c.equipment and c.equipment.plant.id or None
        return result

    @classmethod
    def search_plant(cls, name, clause):
        return [('equipment.plant',) + tuple(clause[1:])]

    @classmethod
    def get_party(cls, component, name):
        result = {}
        for c in component:
            result[c.id] = c.equipment and c.equipment.plant.party.id or None
        return result

    @classmethod
    def search_party(cls, name, clause):
        return [('equipment.plant.party',) + tuple(clause[1:])]

    @fields.depends('type', '_parent_type.product_type')
    def on_change_with_product_type(self, name=None):
        return self.get_product_type([self], name)[self.id]

    @classmethod
    def get_product_type(cls, components, name):
        result = {}
        for c in components:
            result[c.id] = c.type and c.type.product_type.id or None
        return result


class ComercialProductBrand(ModelSQL, ModelView):
    'Comercial Product Brand'
    __name__ = 'lims.comercial.product.brand'

    name = fields.Char('Name', required=True)


class ComercialProduct(ModelSQL, ModelView):
    'Comercial Product'
    __name__ = 'lims.comercial.product'

    name = fields.Char('Name', required=True)
    brand = fields.Many2One('lims.comercial.product.brand', 'Brand',
        required=True)
    matrix = fields.Many2One('lims.matrix', 'Base/Matrix', required=True)
