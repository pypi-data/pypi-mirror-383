import logging

from ms_salesforce_api.salesforce.api.projects_with_backup.constants import (
    DEFAULT_PROJECTS_QUERY,
)
from ms_salesforce_api.salesforce.api.projects_with_backup.dto.ProjectDTO import (  # noqa: E501
    ProjectDTO,
)
from ms_salesforce_api.salesforce.SalesforceQueryExecutor import (
    SalesforceQueryExecutor,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

MAX_PROJECT_IDS_PER_QUERY = 200


class Project(SalesforceQueryExecutor):
    def get_batches(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]  # noqa: E203

    def get_all(
        self,
        query: str = DEFAULT_PROJECTS_QUERY,
        format: str = "json",
    ):
        data = self.fetch_data(query)
        if data is None:
            logging.error(
                "[ERROR - SalesforceAPI]: No projects data return from Salesforce API"  # noqa: E501
            )
            return []

        try:
            projects = [
                ProjectDTO.from_salesforce_record(record) for record in data
            ]
            projects_list = list(projects)

            if format == "json":
                projects_list = [
                    project.to_dict() for project in projects_list
                ]

            return projects_list
        except Exception as e:
            logging.error(
                f"[ERROR - get_all]: Failed to get all projects: {e}"
            )
            return []
