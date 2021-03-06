# This file is part of lims_industry module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool
from . import industry
from . import analysis
from . import sample
from . import party
from . import task


def register():
    Pool.register(
        industry.Plant,
        industry.EquipmentType,
        industry.Brand,
        industry.ComponentType,
        industry.EquipmentTemplate,
        industry.EquipmentTemplateComponentType,
        industry.Equipment,
        industry.Component,
        industry.ComercialProductBrand,
        industry.ComercialProduct,
        analysis.SampleAttributeSet,
        analysis.SampleAttribute,
        analysis.SampleAttributeAttributeSet,
        analysis.SamplingType,
        analysis.ProductType,
        analysis.Analysis,
        sample.Entry,
        sample.Sample,
        sample.CreateSampleStart,
        sample.EditSampleStart,
        party.Party,
        party.Address,
        task.AdministrativeTaskTemplate,
        task.AdministrativeTask,
        module='lims_industry', type_='model')
    Pool.register(
        sample.CreateSample,
        sample.EditSample,
        module='lims_industry', type_='wizard')
