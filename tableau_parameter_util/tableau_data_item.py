from lxml import etree as ET
from typing import List, Mapping
import logging
import sys

from tableau_parameter_util.parameter import Parameter


class TableauDataItem:
    """ Root class for Tableau datasources and workbooks """

    logging.basicConfig(filename="fix.log", level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    def __init__(self, path, params_path):
        self.path = path
        self.tree = ET.parse(path)
        self.parameter: List[Parameter] = []
        self.params_path = params_path
        self.parameters_by_caption: Mapping[str, List[Parameter]] = {}
        self.parameters_by_name: Mapping[str, List[Parameter]] = {}
        self.parameters = self.get_parameters()
        self.is_dirty = False

        for param in self.parameters:
            if param.caption not in self.parameters_by_caption.keys():
                self.parameters_by_caption[param.caption] = [param]
            else:
                self.parameters_by_caption[param.caption].append(param)

        for param in self.parameters:
            if param.name not in self.parameters_by_name.keys():
                self.parameters_by_name[param.name] = [param]
            else:
                self.parameters_by_name[param.name].append(param)

    def get_parameters(self) -> List[Parameter]:
        """ Get a list of parameters"""

        root = self.tree.getroot()
        out_params: List[Parameter] = []
        for parm in root.findall(self.params_path):
            p = Parameter(parm.get("name"), parm.get("caption"), parm.get("datatype"))
            out_params.append(p)
        self.parameters = out_params
        return out_params

    def rename_parameter(self, param_name: str, new_name: str, new_caption: str = None):
        """ Rename a parameter. Need to write to persist."""

        root = self.tree.getroot()

        for parm in root.findall(self.params_path):
            if parm.get("name") == param_name:
                self.is_dirty = True
                parm.set("name", new_name)
                # also rename the caption
                if new_caption:
                    parm.set("caption", new_caption)

    def delete_parameter(self, param_name: str):
        """ Delete a parameter. Need to write to persist."""
        root = self.tree.getroot()

        for parm in root.findall(self.params_path):
            if parm.get("name") == param_name:
                parent = parm.getparent()
                parent.remove(parm)
                self.is_dirty = True

    def get_duplicate_params(self, params: List[Parameter]) -> Mapping[str, List[str]]:
        """ Create a map of duplicate parameters with an array of Parameter.names as
            the values. Also ignore case, since mismatched Caption case also seems to
            cause Tableau to malfunction.
        """
        out_dupes = {}
        seen = set()
        dupes = [x.caption.lower() for x in params if
                 x.caption.lower() in seen or seen.add(x.caption.lower())]

        all_dupes = [x for x in params if x.caption.lower() in dupes]
        for dupe in all_dupes:
            if dupe.caption.lower() in out_dupes.keys():
                out_dupes[dupe.caption.lower()].append(dupe.name)
            else:
                out_dupes[dupe.caption.lower()] = [dupe.name]
        return out_dupes

    def replace_all_in_file(self, search: str, replace: str, output_file: str):
        """ Globally replace a string in a file """

        with open(self.path, 'r') as orig:
            data = orig.read()
            data = data.replace(search, replace)
        with open(output_file, 'w') as output_file:
            output_file.write(data)

    def write(self, output_path: str = None):
        """ Write the XML to disk """

        if output_path:
            self.tree.write(output_path)
            self.is_dirty = False
        else:
            self.tree.write(self.path)
            self.is_dirty = False
