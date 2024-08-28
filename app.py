import logging.config
import sys
from tableau_parameter_util.workbook import Workbook

if __name__ == '__main__':
    logging.config.fileConfig("logging.config")

    input_workbook = "/Users/mike-nacey/Downloads/multids_fix/Throughput Performance " \
                     "Trending ScoreCard.twb"
    wb = Workbook(input_workbook)
    workbook_params = wb.get_parameters()
    print("\n\n===Workbook Params===")
    for parm in workbook_params:
        print(f"{parm.name} - {parm.caption}")

    datasource_params = wb.get_embedded_datasource_params()
    print("\n===Embedded Datasource Params===")
    for ds in datasource_params.keys():
        print(f"DATASOURCE={ds}")
        for param in datasource_params[ds]:
            print(f"\t{param.name} - {param.caption}")

    print("\n===Mismatched Parameters===")
    mismatches = wb.get_mismatched_parameters()
    if len(mismatches) > 0:
        for ds_name, workbook_param, datasource_params in mismatches:
            print(f"WB: {workbook_param.name} - {workbook_param.caption} != "
                  f" DS: [{ds_name}] {datasource_params.name} -"
                  f" {datasource_params.caption}")
        sys.exit(-1)

    else:
        print("--None--")
        sys.exit(0)
