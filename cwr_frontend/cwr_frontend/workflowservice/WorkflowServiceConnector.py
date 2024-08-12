from typing import Any
from urllib.parse import urlencode, urljoin
import requests
from requests.auth import HTTPBasicAuth
import yaml
from django.conf import settings


class WorkflowServiceConnector:

    def __init__(self, base_url=settings.WORKFLOW_SERVICE["URL"], username=settings.WORKFLOW_SERVICE["USER"], password=settings.WORKFLOW_SERVICE["PASSWORD"], verify_ssl=False):
        self._base_url = base_url
        if not self._base_url.endswith("/"):
            self._base_url += "/"
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl

    def check_workflow(self, workflow: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        files = {"file": ("workflow.yaml", yaml.dump(workflow, indent=2))}
        response = requests.post(urljoin(self._base_url, "workflow/check"), files=files, auth=HTTPBasicAuth(self._username, self._password), verify=self._verify_ssl)
        if response.status_code != 200:
            if response.status_code == 400 and "detail" in response.json():
                return False, response.json()
            else:
                response.raise_for_status()
        return True, response.json()

    def submit_workflow(self, workflow: dict[str, Any], title: str, description: str, submitter_name: str, submitter_orcid: str, license: str = None, keywords: list[str] = None, override_parameters: dict[str, str] = None, dry_run: bool = False) -> tuple[bool, dict[str, Any]]:
        if override_parameters is None:
            override_parameters = {}
        if keywords is None:
            keywords = []

        files = {"file": ("workflow.yaml", yaml.dump(workflow, indent=2))}
        form_data = {
            "title": title,
            "description": description,
            "submitterName": submitter_name,
            "submitterOrcid": submitter_orcid,
            "license": license,
            "keywords": ",".join(keywords),
            "overrideParameters": ",".join([f"{key}:{value}" for key, value in override_parameters.items()]),
            "dryRun": dry_run,
        }
        response = requests.post(urljoin(self._base_url, "workflow/submit"), files=files, data=form_data, auth=HTTPBasicAuth(self._username, self._password), verify=self._verify_ssl)
        if response.status_code != 200:
            print(response.text)
            if response.status_code == 400 and "message" in response.json()["detail"]:
                return False, response.json()
            else:
                response.raise_for_status()
        return True, response.json()

    def list_datasets(self, page_size=100, page_num=0) -> list[dict[str, str]]:
        """ retrieve list of objects from cordra """
        params = {
            "pageNum": page_num,
            "pageSize": page_size,
            "query": "type:Dataset",
            "sortFields": 'metadata/modifiedOn DESC '
        }
        url = f'{urljoin(self._base_url, "search")}?{urlencode(params)}'
        response = requests.get(url, verify=False)
        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()
