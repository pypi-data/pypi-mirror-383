import phylogenie.typings as pgt
from phylogenie.models import Distribution, StrictBaseModel
from phylogenie.treesimulator import EventType

Integer = str | int
Scalar = str | pgt.Scalar
ManyScalars = str | pgt.Many[Scalar]
OneOrManyScalars = Scalar | pgt.Many[Scalar]
OneOrMany2DScalars = Scalar | pgt.Many2D[Scalar]


class SkylineParameterModel(StrictBaseModel):
    value: ManyScalars
    change_times: ManyScalars


class SkylineVectorModel(StrictBaseModel):
    value: str | pgt.Many[OneOrManyScalars]
    change_times: ManyScalars


class SkylineMatrixModel(StrictBaseModel):
    value: str | pgt.Many[OneOrMany2DScalars]
    change_times: ManyScalars


SkylineParameter = Scalar | SkylineParameterModel
SkylineVector = str | pgt.Scalar | pgt.Many[SkylineParameter] | SkylineVectorModel
SkylineMatrix = str | pgt.Scalar | pgt.Many[SkylineVector] | SkylineMatrixModel | None


class Event(StrictBaseModel):
    state: str | None = None
    rate: SkylineParameter


class Mutation(Event):
    rate_scalers: dict[EventType, Distribution]
