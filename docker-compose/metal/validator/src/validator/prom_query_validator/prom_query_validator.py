from prometheus_api_client import PrometheusConnect
from typing import Tuple, List
from datetime import datetime
import numpy as np
import statistics

#TODO: Include Environment Variables if desired
class PromMetricsValidator:
    def __init__(self, endpoint: str, headers=None, disable_ssl=True) -> None:
        self.prom_client = PrometheusConnect(endpoint, headers=None, disable_ssl=disable_ssl)
        
    @staticmethod
    def merge_prom_metric_list(prom_query_result: list) -> List[Tuple[str, float]]:
        cleaned_data = []
        for index, query in enumerate(prom_query_result):
            for element in query["values"]:
                if index == 0:
                    cleaned_data.append( [element[0], float(element[1])] )
                else:
                    cleaned_data[index][1] += float(element[1])
        return cleaned_data
    
    
    @staticmethod
    def disjunct_prom_datapoints(prom_data_list_one, prom_data_list_two) -> Tuple[list, list]:
        common_timestamps = [datapoint[0] for datapoint in prom_data_list_one if datapoint[0] in [datapoint[0] for datapoint in prom_data_list_two]]
        list_one_metrics = []
        list_two_metrics = []
        for timestamp in common_timestamps:
            for list_one_datapoint in prom_data_list_one:
                if list_one_datapoint[0] == timestamp:
                    list_one_metrics.append(list_one_datapoint[:])
            for list_two_datapoint in prom_data_list_two:
                if list_two_datapoint[0] == timestamp:
                    list_two_metrics.append(list_two_datapoint[:])
        return list_one_metrics, list_two_metrics


    def compare_metrics(self, start_time: datetime, end_time: datetime, expected_query: str, expected_query_labels: dict, actual_query: str, actual_query_labels: dict) -> Tuple[List[float], List[float]]:
        # parsed_start_time = parse_datetime(start_time)
        # if parsed_start_time is None:
        #     raise ValueError("Invalid start time")
        #
        # parsed_end_time = parse_datetime(end_time)
        # if parsed_end_time is None:
        #     raise ValueError("Invalid end time")


        expected_metrics = self.prom_client.get_metric_range_data(
            metric_name=expected_query,
            label_config=expected_query_labels.copy(),
            start_time=start_time,
            end_time=end_time,
        )

        actual_metrics = self.prom_client.get_metric_range_data(
            metric_name=actual_query,
            label_config=actual_query_labels.copy(),
            start_time=start_time,
            end_time=end_time,
        )
        # clean data to acquire only lists
        expected_data = self.merge_prom_metric_list(expected_metrics)
        actual_data = self.merge_prom_metric_list(actual_metrics)
        
        # remove timestamps that do not match
        return self.disjunct_prom_datapoints(expected_data, actual_data)


def absolute_percentage_error(expected_data, actual_data) -> List[float]:
    expected_data = np.array(expected_data)
    actual_data = np.array(actual_data)

    absolute_percentage_error = np.abs((expected_data - actual_data) / expected_data) * 100
    return absolute_percentage_error.tolist()


def absolute_error(expected_data, actual_data) -> List[float]:
    expected_data = np.array(expected_data)
    actual_data = np.array(actual_data)

    absolute_error = np.abs(expected_data - actual_data)
    return absolute_error.tolist()


def mean_absolute_error(expected_data, actual_data) -> float:
    return statistics.mean(absolute_error(expected_data, actual_data))


def mean_absolute_percentage_error(expected_data, actual_data) -> float:
    return statistics.mean(absolute_percentage_error(expected_data, actual_data))



# if __name__ == "__main__":
#     prom_metrics_validator = PromMetricsValidator("http://localhost:9091")
#     start_datetime = datetime.strptime("2024-04-10 19:17:53.882176", '%Y-%m-%d %H:%M:%S.%f')
#     end_datetime = datetime.strptime("2024-04-10 19:21:36.320520", '%Y-%m-%d %H:%M:%S.%f')
#     cleaned_validator_data, cleaned_validated_data = prom_metrics_validator.retrieve_energy_metrics_with_queries(
#         start_time=start_datetime,
#         end_time=end_datetime,
#         expected_query="kepler_process_package_joules_total{command='qemu-system-x86'}",
#         actual_query="kepler_node_platform_joules_total{job='vm'}"
#     )
#     # cleaned_validator_data = []
#     # for element in validator_data[0]["values"]:
#     #     cleaned_validator_data.append(float(element[1]))
#     # for element in validator_data[1]["values"]:
#     #     cleaned_validator_data.append(float(element[1]))
#
#     # cleaned_validated_data = []
#     # for element in validated_data[0]["values"]:
#     #     cleaned_validated_data.append(float(element[1]))
#     print(len(cleaned_validator_data))
#     print(len(cleaned_validated_data))
#     print(deltas_func(cleaned_validator_data, cleaned_validated_data))
#     print(percentage_err(cleaned_validator_data, cleaned_validated_data))
#
    
