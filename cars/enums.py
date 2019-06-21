from enumfields import Enum


class CarType(Enum):
    normal = 'normal'
    hatchback = 'hatchback'
    sedan = 'sedan'
    suv = 'suv'
    commercial = 'commercial'
    minibus = 'minibus'

    class Labels:
        normal = 'Normal'
        hatchback = 'Hatchback'
        sedan = 'Sedan'
        suv = 'Suv'
        commercial = 'Commercial'
        minibus = 'Minibus'
