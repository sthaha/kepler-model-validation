from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime
from typing import Tuple, List
from datetime import datetime

#TODO: Include Environment Variables if desired
class PromMetricsValidator:

    # metric_type_validator_to_metric_type_validated = {
    #     "process_power_qemu_system_kepler_bm": "platform_power_qemu_kepler_vm" 
    # }

    # metric_type_to_prom_query = {
    #     "process_power_qemu_system_kepler_bm": "",
    #     "platform_power_qemu_kepler_vm": ""
    # }

    def __init__(self, prom_endpoint: str, headers=None, disable_ssl=True) -> None:
        self.prom_client = PrometheusConnect(prom_endpoint, headers, disable_ssl)
        

    def retrieve_energy_metrics_with_queries(self, start_time, end_time, validator_query, validated_query) -> Tuple[List[float], List[float]]:
        parsed_start_time = parse_datetime(start_time)
        parsed_end_time = parse_datetime(end_time)
        validator_data = self.prom_client.get_metric_range_data(
            validator_query,
            start_time=parsed_start_time,
            end_time=parsed_end_time,
        )

        validated_data = self.prom_client.get_metric_range_data(
            validated_query,
            start_time=parsed_start_time,
            end_time=parsed_end_time,
        )
        # clean data to acquire only lists
        cleaned_validator_data = []
        for query in validator_data:
            for index, element in enumerate(query["values"]):
                if len(cleaned_validator_data) < index + 1:
                    cleaned_validator_data.append(float(element[1]))
                else:
                    cleaned_validator_data[index] += float(element[1])
        cleaned_validated_data = []
        for query in validated_data:
            for index, element in enumerate(query["values"]):
                if len(cleaned_validated_data) < index + 1:
                    cleaned_validated_data.append(float(element[1]))
                else:
                    cleaned_validated_data[index] += float(element[1])
        return cleaned_validator_data, cleaned_validated_data


def deltas_func(validator_data, validated_data) -> List[float]:
    delta_list = []
    for validator_element, validated_element in zip(validator_data, validated_data):
        delta_list.append(abs(validator_element - validated_element))
    return delta_list

def percentage_err(validator_data, validated_data) -> List[float]:
    percentage_err_list = []
    for validator_element, validated_element in zip(validator_data, validated_data):
        percentage_err_list.append(abs((validator_element - validated_element) / validator_element) * 100)
    return percentage_err_list


if __name__ == "__main__":
    prom_metrics_validator = PromMetricsValidator("http://localhost:9091")
    start_datetime = datetime.strptime("2024-04-10 19:17:53.882176", '%Y-%m-%d %H:%M:%S.%f')
    end_datetime = datetime.strptime("2024-04-10 19:21:36.320520", '%Y-%m-%d %H:%M:%S.%f')
    cleaned_validator_data, cleaned_validated_data = prom_metrics_validator.retrieve_energy_metrics_with_queries(
        start_time=start_datetime,
        end_time=end_datetime,
        validator_query="kepler_process_package_joules_total{command='qemu-system-x86'}",
        validated_query="kepler_node_platform_joules_total{job='vm'}"
    )
    # cleaned_validator_data = []
    # for element in validator_data[0]["values"]:
    #     cleaned_validator_data.append(float(element[1]))
    # for element in validator_data[1]["values"]:
    #     cleaned_validator_data.append(float(element[1]))
    
    # cleaned_validated_data = []
    # for element in validated_data[0]["values"]:
    #     cleaned_validated_data.append(float(element[1]))
    print(len(cleaned_validator_data))
    print(len(cleaned_validated_data))
    print(deltas_func(cleaned_validator_data, cleaned_validated_data))
    print(percentage_err(cleaned_validator_data, cleaned_validated_data))

    
