
from tableau_parameter_util.tableau_data_item import TableauDataItem


class Datasource (TableauDataItem):
    """ Tableau datasource class. Also used as a base for common functions"""
    PARAMS_PATH = '''./datasource-dependencies[
        @datasource='Parameters']/column'''

    def __init__(self, path):
        super().__init__(path, self.PARAMS_PATH)



