
from dataclasses import dataclass


@dataclass
class H2COption:
    name : str
    description : str = None
    default : str = None
    typeOfVar : str = None
    isFlag : bool = False
    isRequired : bool = False

@dataclass
class H2CCommand:
    name : str
    args : list[str]
    options : dict[str, H2COption]
    # separated by . for sub groups
    group : str = None
