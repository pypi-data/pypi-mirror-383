"""
This file contains the CPUConfig dataclass.
Defines the CPU configuration used in the system.
"""

from dataclasses import asdict, dataclass, field


@dataclass
class BaseDataClass:
    kind: str = field(init=False)

    def __post_init__(self):
        self.kind = self.__class__.__name__

    def as_dict(self):
        return asdict(self)


@dataclass
class CPUConfig(BaseDataClass):
    """
    Enum for CPU types.
    These are all the CPU types that are supported by the system.
    """

    cpu_count: int
    memory_count: int

    def __post_init__(self):
        super().__post_init__()
        allowed_cpu_counts = {1, 2}
        allowed_memory_counts = {2, 4, 8}
        if self.cpu_count not in allowed_cpu_counts:
            raise ValueError(
                f"Invalid cpu_count: {self.cpu_count}. Allowed values are {sorted(allowed_cpu_counts)}."
            )
        if self.memory_count not in allowed_memory_counts:
            raise ValueError(
                f"Invalid memory_count: {self.memory_count}. Allowed values are {sorted(allowed_memory_counts)}."
            )


# Alias to mirror the TypeScript type name
CPUSpecification = CPUConfig
