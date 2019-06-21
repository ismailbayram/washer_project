from enumfields import Enum


class CarType(Enum):
    normal = 'normal'
    hatchback = 'hatchback'
    sedan = 'sedan'
    suv = 'suv'
    ticari = 'ticari'
    minibus = 'minibus'

    class Labels:
        normal = 'Normal'
        hatchback = 'Hatchback'
        sedan = 'Sedan'
        suv = 'Suv'
        ticari = 'Ticari'
        minibus = 'Minibus'
