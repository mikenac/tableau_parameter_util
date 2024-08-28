from typing import Mapping, List, Tuple
from lxml import etree as ET
import re

from tableau_parameter_util.datasource import Datasource
from tableau_parameter_util.parameter import Parameter
from tableau_parameter_util.tableau_data_item import TableauDataItem


class Workbook(TableauDataItem):
    """ Tableau datasource class. Also used as a base for common functions"""
    PARAMS_PATH = '''./datasources/datasource[@name='Parameters']/column'''

    def __init__(self, path):
        super().__init__(path, self.PARAMS_PATH)

    def get_embedded_datasource_params(self) -> Mapping[str, List[Parameter]]:
        """ Parse embedded datasource copy to get parameters """

        root = self.tree.getroot()
        # do not wrap line or it breaks. Dunno why yet.
        ds = root.findall(
            '''./datasources/datasource/connection/metadata-records/metadata-record[@class='capability']/attributes/attribute[@name='datasource']''')

        out_params_map = {}

        for embedded_ds in ds:

            # Cleanup garbage XML or this won't parse. I have no idea where this
            # encoding comes from, but it's garbage. Remove double quotes surrounding
            # the CDATA
            embedded = embedded_ds.text.strip('"')
            # Remove a forward slash before pound
            embedded = re.sub(r"\\#", r"#", embedded)
            # Remove a colon that is prefixing an attribute
            embedded = re.sub(r":(\w)", "\\1", embedded)

            ele = ET.fromstring(str.encode(embedded))
            ds_name = ele.get("formatted-name")
            out_params_map[ds_name] = []

            for parm in ele.findall(Datasource.PARAMS_PATH):
                p = Parameter(parm.get("name"),
                              parm.get("caption"),
                              parm.get("datatype"))

                out_params_map[ds_name].append(p)

        return out_params_map

    def get_mismatched_parameters(self) -> List[Tuple[str, Parameter, Parameter]]:
        """ Get parameters where the caption matches the datasource, but the name is
            different.
            Outputs a list of mismatches where the first tuple is the workbook param
            and the second tuple is the datasource param.
        """

        workbook_params = self.get_parameters()
        datasource_params = self.get_embedded_datasource_params()

        mismatched = []
        for workbook_param in workbook_params:
            for ds in datasource_params.keys():
                for datasource_param in datasource_params[ds]:
                    if workbook_param.caption.lower() == \
                            datasource_param.caption.lower() \
                            and workbook_param.name != datasource_param.name:
                        mismatched.append((ds, workbook_param, datasource_param))
        return mismatched
