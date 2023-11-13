# need a way to distinguish between timestamp outputs -- assume chronological
# how do we quantify quality gained by finer granularity?
from test.error_measures import error_measurers


class HysplitResult:
    def __init__(self, path: str = "", parameters: dict = None):
        self.parameters = {
            "%spacing%": "",
            "%sampling%": "",
            "%grid_center%": "",
            "%span%": ""
        }
        if parameters is None:
            self.parameters = parameters
        self.path = path
        self.results = [dict()]

    def set_parameter(self, name: str, value: str) -> None:
        self.parameters[name] = value

    def fetch_results(self) -> [dict]:
        return self.results


def compare_quality(test_config: dict, ground_truth_config: dict = None):
    test_result = HysplitResult(test_config["path"], test_config["parameters"])
    test_result.fetch_results()
    ground_truth_result = HysplitResult(ground_truth_config["path"], ground_truth_config["parameters"])
    ground_truth_result.fetch_results()
    compute_error(test_result, ground_truth_result)


def compute_error(dataset1: HysplitResult, dataset2: HysplitResult, error_type: str = "mae"):
    spacing1 = float(dataset1.parameters["%spacing%"])
    spacing2 = float(dataset2.parameters["%spacing%"])
    dataset_fine, dataset_coarse = dataset1, dataset2
    if spacing1 > spacing2:
        dataset_fine, dataset_coarse = dataset2, dataset1
        spacing1, spacing2 = spacing2, spacing1
    if spacing2 / spacing1 != 0:
        raise Exception("Cannot compare: the smaller spacing does not divide the larger spacing")
    errors = list()
    for row in dataset_coarse.results:
        relevant_fine_data = get_matching_data(row, dataset_coarse.parameters, dataset_fine)
        errors.append(error_measurers[error_type](row, relevant_fine_data))


def get_matching_data(row: dict, parameters: dict, dataset: [dict]) -> [dict]:
    # need a way to match cells between lower and higher resolution --
    #     given coordinates and spacing,
    #     find the smaller cells that fit in the bigger one
    pass
