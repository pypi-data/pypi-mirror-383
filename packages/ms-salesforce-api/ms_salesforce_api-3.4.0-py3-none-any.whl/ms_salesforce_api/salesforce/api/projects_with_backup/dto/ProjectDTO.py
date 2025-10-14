from ms_salesforce_api.salesforce.helpers.string import normalize_value


class ProjectDTO(object):
    def __init__(
        self,
        id,
        account_customer_group_name,
        account_name,
        project_name,
        project_code,
        project_status,
        project_startdate,
        project_enddate,
        account_manager_name,
        account_billing_country,
        division,
    ):
        self.id = id
        self.account_customer_group_name = account_customer_group_name
        self.account_name = account_name
        self.project_name = project_name
        self.project_code = project_code
        self.project_status = project_status
        self.project_startdate = project_startdate
        self.project_enddate = project_enddate
        self.account_manager_name = account_manager_name
        self.account_billing_country = account_billing_country
        self.division = division

    @staticmethod
    def from_salesforce_record(record):
        def _get_account_customer_group_name():
            try:
                return normalize_value(
                    record["Account"]["LKP_CustomerSubgroup__r"][
                        "LKP_CustomerGroup__r"
                    ][
                        "Name"
                    ]  # noqa: E501
                )
            except (KeyError, TypeError):
                return None

        def _get_account_name():
            try:
                return normalize_value(record["Account"]["Name"])  # noqa: E501
            except (KeyError, TypeError):
                return None

        def _get_account_manager_name():
            try:
                return normalize_value(
                    record["LKP_AccountManager__r"]["Name"]  # noqa: E501
                )
            except (KeyError, TypeError):
                return None

        return ProjectDTO(
            id=record["Id"],
            account_customer_group_name=_get_account_customer_group_name(),
            account_name=_get_account_name(),
            project_name=record["FRM_ProjectName__c"],
            project_code=record["FRM_ProjectCode__c"],
            project_status=record["PCK_ProjectStatus__c"],
            project_startdate=record["DT_ProjectStartDate__c"],
            project_enddate=record["DT_ProjectEndDate__c"],
            account_manager_name=_get_account_manager_name(),
            account_billing_country=record["Account_Billing_Country__c"],
            division=record["PCK_Division__c"],
        )

    def to_dict(self):
        return {
            "id": self.id,
            "account_customer_group_name": self.account_customer_group_name,
            "account_name": self.account_name,
            "project_name": self.project_name,
            "project_code": self.project_code,
            "project_status": self.project_status,
            "project_startdate": self.project_startdate,
            "project_enddate": self.project_enddate,
            "account_manager_name": self.account_manager_name,
            "account_billing_country": self.account_billing_country,
            "division": self.division,
        }
