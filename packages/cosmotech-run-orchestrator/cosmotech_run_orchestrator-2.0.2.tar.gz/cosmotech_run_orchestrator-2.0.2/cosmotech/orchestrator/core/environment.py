# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import os
from dataclasses import dataclass
from dataclasses import field


@dataclass
class EnvironmentVariable:
    name: str = field(repr=False)
    defaultValue: str = field(default=None)
    value: str = field(default=None)
    description: str = field(default=None)
    optional: bool = field(default=False)

    def is_required(self):
        return (not self.value and not self.defaultValue) and not self.optional

    def effective_value(self):
        v = self.value or os.environ.get(self.name, self.defaultValue)
        if v is not None:
            return str(v)
        return None

    def join(self, other: "EnvironmentVariable"):
        self.defaultValue = self.defaultValue or other.defaultValue
        self.value = self.value or other.value
        self.description = self.description or other.description
        self.optional = self.optional or other.optional

    def serialize(self):
        r = {}
        if self.value:
            r["value"] = self.value
        if self.defaultValue:
            r["defaultValue"] = self.defaultValue
        if self.description:
            r["description"] = self.description
        if self.optional:
            r["optional"] = self.optional
        return r
