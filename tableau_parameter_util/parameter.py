from dataclasses import dataclass


@dataclass
class Parameter:
    """ A workbook or datasource parameter """
    name: str
    caption: str
    data_type: str
