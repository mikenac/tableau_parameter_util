from dataclasses import dataclass


@dataclass
class Parameter:
    """ A workbook or datasource parameter """
    name: str
    caption: str
    data_type: str
    # def __init__(self, name: str, caption: str, datatype: str):
    #     self.name = name
    #     self.caption = caption
    #     self.datatype = datatype
