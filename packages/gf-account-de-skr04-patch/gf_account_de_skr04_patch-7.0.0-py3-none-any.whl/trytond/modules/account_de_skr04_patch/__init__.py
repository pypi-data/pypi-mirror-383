from trytond.pool import Pool

__all__ = ['register']


def register():
    Pool.register(
        module='account_de_skr04_patch', type_='model')
    Pool.register(
        module='account_de_skr04_patch', type_='wizard')
    Pool.register(
        module='account_de_skr04_patch', type_='report')
