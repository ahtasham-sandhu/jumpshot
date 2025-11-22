from rococo.models import Person as BasePerson
from typing import ClassVar
from dataclasses import dataclass

@dataclass
class Person(BasePerson):
    use_type_checking: ClassVar[bool] = True
