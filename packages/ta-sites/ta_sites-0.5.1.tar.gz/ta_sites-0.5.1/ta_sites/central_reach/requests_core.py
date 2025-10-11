import datetime
import json
import requests
from retry import retry
from .exceptions import BadRequestError, ScheduledMaintenanceError


def retry_if_bad_request(func):
    attempt = 1
    tries = 3

    @retry(exceptions=BadRequestError, tries=tries, delay=1, backoff=2)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BadRequestError as ex:
            nonlocal attempt
            print(f"Bad request Attempt {attempt}...", "WARN")
            attempt = attempt + 1 if attempt < tries else 1
            raise ex

    return wrapper


class CentralReachRequestsCore:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ):
        """
        CentralReachRequestsCore object. Please Inheritance it.

        :param login: login for CentralReach site.
        :param password: password for CentralReach site.
        :param captcha_api_key: api_key for captcha solver - can be just api_key itself or (provider, api_key) tuple.
        """
        self.session = requests.sessions.Session()
        _ = self._get_internal_cookie(self._get_auth_token(client_id, client_secret).json())
        self._session_csrf_token = self.session.cookies["csrf-token"]

    def _get_headers(self, is_json=True, add_headers: dict = None, put_token: bool = True) -> dict:
        """
        Prepare header object for request.

        :param is_json (bool): True if content-type should be json, else False.
        :param add_headers (dict): dictionary with key-values that should be added to headers.
        :param put_token (bool): True if 'csrf-token' should be added to headers, else False.
        """
        headers = {"origin": "https://members.centralreach.com"}
        if is_json:
            headers["content-type"] = "application/json; charset=UTF-8"

        if put_token:
            headers["x-csrf-token"] = self._session_csrf_token

        if add_headers:
            for key, value in add_headers.items():
                headers[key] = value
        return headers

    @staticmethod
    def __is_scheduled_maintenance(response) -> bool:
        if response.status_code == 200 and "scheduled maintenance" in response.text.lower():
            return True
        return False

    @staticmethod
    def _is_json_response(response) -> bool:
        try:
            response.json()
            return True
        except json.decoder.JSONDecodeError:
            return False

    def check_response(
        self, response, mandatory_json: bool = False, exc_message: str = "", re_authorize: bool = True
    ) -> None:
        """
        This method check response and raise exception 'BadRequestError'
           or 'ScheduledMaintenanceError' with exc_message,
        If status code is 401 (unauthorized) then it will try login again
        :param response: response from request
        :param mandatory_json: bool, if True - it will check is response contain json data
        :param exc_message: text message which will be raise if response wrong
        :param re_authorize: bool, if True then it will try login again if status code is 401
        """
        # Check if site is under scheduled maintenance
        if self.__is_scheduled_maintenance(response):
            print(exc_message, "Error")
            print("'Central Reach' site is currently unavailable due to scheduled maintenance", "Error")
            raise ScheduledMaintenanceError

        # Check if response is unauthorized
        if response.status_code == 401:
            unauthorized_request = True
        elif self._is_json_response(response) and response.json().get("message", "") == "Not logged in.":
            unauthorized_request = True
        else:
            unauthorized_request = False

        if unauthorized_request:
            if re_authorize:
                self._login_to_central_reach()
            raise BadRequestError(
                f"{exc_message}Status Code: {response.status_code} (Unauthorized request), "
                f"Json content: {response.json()}, Headers: {response.headers}"
            )

        # Check if response is not 200 or not json
        if response.status_code != 200 or (mandatory_json and not self._is_json_response(response)):
            exc_message = exc_message + "\n" if exc_message else ""
            if self._is_json_response(response):
                raise BadRequestError(
                    f"{exc_message}Status Code: {response.status_code}, "
                    f"Json content: {response.json()}, Headers: {response.headers}"
                )
            else:
                raise BadRequestError(
                    f"{exc_message}Status Code: {response.status_code}, " f"Headers: {response.headers}"
                )

    def _get_auth_token(self, client_id, client_secret):
        """Retrieve the authentication token."""
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "cr-api",
        }

        return self.session.post("https://login.centralreach.com/connect/token", data=data)

    def _get_internal_cookie(self, jwt):
        """Exchange the authentication token for an internal session cookie."""
        headers = {
            "Accept": "application/json",
        }

        json_data = {
            "token": jwt["access_token"],
        }

        return self.session.post(
            "https://members.centralreach.com/api/?framework.authtoken", headers=headers, json=json_data
        )

    def __insurance_eligibility_status(self) -> None:
        header = {"referer": "https://members.centralreach.com/"}
        url = "https://members.centralreach.com/crxapi/system/dictionary/InsuranceEligibilityStatus"
        response = self.session.get(url, headers=self._get_headers(is_json=True, add_headers=header))

        exception_message = "Problems with insurance eligibility request."
        self.check_response(response, mandatory_json=True, exc_message=exception_message, re_authorize=False)

    @retry_if_bad_request
    def _get_filters(self):
        payload = {
            "applicationSection": "billingmanager.billing",
        }
        url = "https://members.centralreach.com/api/?shared.loadFilters"
        response = self.session.post(url, json=payload, headers=self._get_headers(is_json=True))

        exception_message = "Problems with getting billings."
        self.check_response(response, mandatory_json=True, exc_message=exception_message)
        return response.json()["filters"]

    def get_filter_by_name(self, filter_name):
        filters = self._get_filters()
        for filter_data in filters:
            if str(filter_data["Name"]).strip() == filter_name:
                return json.loads(filter_data["filters"])
        else:
            raise Exception("Filter '{filter_name}' doesn't exist")

    @retry_if_bad_request
    def get_era_list(self, start_date: datetime = None, end_date: datetime = None):
        _start_date = start_date.strftime("%Y-%m-%d") if start_date else ""
        _end_date = end_date.strftime("%Y-%m-%d") if start_date else ""

        load_era_list_url = "https://members.centralreach.com/api/?claims.loadERAList"
        data = {
            "startDate": _start_date,
            "endDate": _end_date,
            "page": "1",
            "claimLabelId": "",
            "pageSize": "2000",
        }
        response = self.session.get(load_era_list_url, json=data, headers=self._get_headers(is_json=False))
        if response.status_code != 200:
            response = self.session.get(load_era_list_url, json=data, headers=self._get_headers(is_json=False))

        if "application/json" in response.headers.get("content-type"):
            if response.status_code == 200 and response.json().get("success", False) is True:
                return response.json()
            elif "message" in response.json():
                raise Exception(
                    f"Problems with getting 'Era List' from 'Central Reach' site. {response.json()['message']}"
                )
        raise Exception("Problems with getting 'Era List' from 'Central Reach' site.")

    def get_zero_pay_filter(self, start_date: datetime = None, end_date: datetime = None) -> dict:
        response = self.get_era_list(start_date, end_date)
        era_list_data = response["items"]

        # Zero Pay filter
        zero_pay_data: dict = {}
        for item in era_list_data:
            if item["PaymentAmount"] == 0.0:
                zero_pay_data[str(item["Id"])] = item
        return zero_pay_data

    def get_pr_filter(self, start_date: datetime = None, end_date: datetime = None) -> dict:
        response = self.get_era_list(start_date, end_date)
        era_list_data = response["items"]

        # PR filter
        pr_data: dict = {}
        for item in era_list_data:
            if (
                item["PaymentAmount"] == 0.0
                and item["PrAdjustmentTotal"] > 0
                and item["PiAdjustmentTotal"] == 0.0
                and item["Reconciled"] == "None"
            ):
                pr_data[str(item["Id"])] = item
        return pr_data

    def get_denial_filter(self, start_date: datetime = None, end_date: datetime = None) -> dict:
        response = self.get_era_list(start_date, end_date)
        era_list_data = response["items"]

        # Denial filter
        denial_data: dict = {}
        for item in era_list_data:
            if item["PaymentAmount"] == 0.0 and item["Reconciled"] == "None":
                denial_data[str(item["Id"])] = item
        return denial_data
