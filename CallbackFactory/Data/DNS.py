from dataclasses import dataclass
from uuid import UUID

memory = {}


@dataclass(frozen=True)
class Data:
    ...


@dataclass(frozen=True)
class AddRecData(Data):
    zone_id: str
    data: dict


@dataclass(frozen=True)
class GetRecInfoData(Data):
    zone_id: str
    record_id: str


@dataclass(frozen=True)
class DelRecData(Data):
    zone_id: str
    record_id: str


@dataclass(frozen=True)
class DelRecConfirmData(Data):
    zone_id: str
    record_id: str


def write_id(key: UUID, data: Data) -> None:
    global memory
    memory[key] = data
