import requests.exceptions


def get_api_response_data(response: requests.Response,
                          start_time: [str, float, int],
                          end_time: [str, float, int]) -> dict:
    """
    use requests response to create data dict
    :param response: requests response
    :param start_time: test start time
    :param end_time: test end time
    :return: data dict include [status_code, text, content, headers, history, encoding, cookies,
    elapsed, request_time_sec, request_method, request_url, request_body, start_time, end_time]
    """
    response_data = {
        "status_code": response.status_code,
        "text": response.text,
        "content": response.content,
        "headers": response.headers,
        "encoding": response.encoding,
        "request_method": response.request.method,
        "request_url": response.request.url,
        "request_body": response.request.body,
        "start_time": start_time,
        "end_time": end_time
    }
    try:
        if response_data.get("status_code") == 200:
            response_data.update({"json": response.json()})
        else:
            response_data.update({"json": None})
    except requests.exceptions.JSONDecodeError:
        response_data.update({"json": None})
    return response_data
