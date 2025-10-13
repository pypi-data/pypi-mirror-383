import json
import sys
from threading import Lock

from je_load_density.utils.exception.exception_tags import cant_generate_json_report
from je_load_density.utils.exception.exceptions import LoadDensityGenerateJsonReportException
from je_load_density.utils.test_record.test_record_class import test_record_instance


def generate_json():
    if len(test_record_instance.test_record_list) == 0 and len(test_record_instance.error_record_list) == 0:
        raise LoadDensityGenerateJsonReportException(cant_generate_json_report)
    else:
        success_dict = dict()
        failure_dict = dict()
        failure_count: int = 1
        failure_test_str: str = "Failure_Test"
        success_count: int = 1
        success_test_str: str = "Success_Test"
        for record_data in test_record_instance.test_record_list:
            success_dict.update(
                {
                    success_test_str + str(success_count): {
                        "Method": str(record_data.get("Method")),
                        "test_url": str(record_data.get("test_url")),
                        "name": str(record_data.get("name")),
                        "status_code": str(record_data.get("status_code")),
                        "text": str(record_data.get("text")),
                        "content": str(record_data.get("content")),
                        "headers": str(record_data.get("headers"))
                    }
                }
            )
            success_count = success_count + 1
        for record_data in test_record_instance.error_record_list:
            failure_dict.update(
                {
                    failure_test_str + str(failure_count): {
                        "Method": str(record_data.get("Method")),
                        "test_url": str(record_data.get("test_url")),
                        "name": str(record_data.get("name")),
                        "status_code": str(record_data.get("status_code")),
                        "error": str(record_data.get("error"))
                    }
                }
            )
            failure_count = failure_count + 1
    return success_dict, failure_dict


def generate_json_report(json_file_name: str = "default_name"):
    """
    :param json_file_name: save json file's name
    """
    lock = Lock()
    success_dict, failure_dict = generate_json()
    try:
        lock.acquire()
        with open(json_file_name + "_success.json", "w+") as file_to_write:
            json.dump(dict(success_dict), file_to_write, indent=4)
    except Exception as error:
        print(repr(error), file=sys.stderr)
    finally:
        lock.release()
    try:
        lock.acquire()
        with open(json_file_name + "_failure.json", "w+") as file_to_write:
            json.dump(dict(failure_dict), file_to_write, indent=4)
    except Exception as error:
        print(repr(error), file=sys.stderr)
    finally:
        lock.release()
