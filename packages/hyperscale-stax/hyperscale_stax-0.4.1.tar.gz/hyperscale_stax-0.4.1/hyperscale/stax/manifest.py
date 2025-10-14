from dataclasses import dataclass
from dataclasses import field
from datetime import date
from enum import Enum
from pathlib import Path

import yaml


class ManifestError(Exception):
    """Raised when the manifest is invalid."""


class DeployMethod(str, Enum):
    STACK_SET = "stack_set"
    STACK = "stack"
    RCP = "rcp"
    SCP = "scp"

    @classmethod
    def from_value(cls, value: str) -> "DeployMethod":
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(value)

    @classmethod
    def list_values(cls) -> list[str]:
        return [m.value for m in cls]


@dataclass
class Parameter:
    parameter_key: str
    parameter_value: str

    @staticmethod
    def from_dict(data: dict) -> "Parameter":
        try:
            key = data["parameter_key"]
            value = data["parameter_value"]
        except KeyError as exc:
            raise ManifestError(f"missing parameter field: {exc}") from exc
        if not isinstance(key, str):
            raise ManifestError("parameter_key must be a string")
        return Parameter(
            parameter_key=key,
            parameter_value=str(value),
        )


@dataclass
class DeploymentTargets:
    accounts: list[str] = field(default_factory=list)
    organizational_units: list[str] = field(default_factory=list)

    @staticmethod
    def from_dict(data: dict, service_managed_perms: bool) -> "DeploymentTargets":
        if service_managed_perms:
            # These rules are nasty but blame the AWS API
            if "organizational_units" not in data:
                raise ManifestError(
                    "organizational_units must be specified when using service managed "
                    "permissions. If you want to target specific accounts you still "
                    "need to list an ou that the account is in."
                )
        else:
            if "organizational_units" in data:
                raise ManifestError(
                    "Cannot specify organizational_units when using self-managed "
                    "permissions."
                )
            if "accounts" not in data:
                raise ManifestError(
                    "Must specify accounts when using self-managed permissions."
                )

        raw_accounts = data.get("accounts", [])
        raw_ous = data.get("organizational_units", [])

        if raw_accounts is None:
            raw_accounts = []
        if raw_ous is None:
            raw_ous = []

        if not isinstance(raw_accounts, list):
            raise ManifestError("deployment_targets.accounts must be a list")
        if not isinstance(raw_ous, list):
            raise ManifestError(
                "deployment_targets.organizational_units must be a list"
            )

        # Normalize accounts to strings to preserve any leading zeros
        # if provided
        accounts = [str(a) for a in raw_accounts]
        organizational_units = [str(o) for o in raw_ous]

        return DeploymentTargets(
            accounts=accounts,
            organizational_units=organizational_units,
        )


@dataclass
class Resource:
    name: str
    resource_file: str
    deployment_targets: DeploymentTargets
    deploy_method: DeployMethod
    regions: list[str]
    parameters: list[Parameter] = field(default_factory=list)

    @staticmethod
    def from_dict(data: dict, service_managed_perms: bool) -> "Resource":
        required_fields = [
            "name",
            "resource_file",
            "deploy_method",
            "regions",
        ]
        for f in required_fields:
            if f not in data:
                raise ManifestError(f"resource missing required field '{f}'")

        name = data["name"]
        resource_file = data["resource_file"]
        deploy_method = data["deploy_method"]
        regions = data["regions"]

        # deployment_targets is only required for stack_set deployment method
        if "deployment_targets" not in data:
            if DeployMethod.from_value(deploy_method) == DeployMethod.STACK_SET:
                raise ManifestError(
                    "resource missing required field 'deployment_targets' "
                    "for stack_set deployment method"
                )
            # For stack deployment method, create empty deployment targets
            deployment_targets = DeploymentTargets()
        else:
            deployment_targets = DeploymentTargets.from_dict(
                data["deployment_targets"], service_managed_perms
            )

        if not isinstance(name, str):
            raise ManifestError("resource.name must be a string")
        if not isinstance(resource_file, str):
            raise ManifestError("resource.resource_file must be a string")
        try:
            method_enum = DeployMethod.from_value(deploy_method)
        except ValueError as exc:
            raise ManifestError(
                "resource.deploy_method must be one of: "
                f"{', '.join(DeployMethod.list_values())}"
            ) from exc
        if not isinstance(regions, list) or not all(
            isinstance(r, str) for r in regions
        ):
            raise ManifestError("resource.regions must be a list of strings")

        parameters_data = data.get("parameters", [])
        if parameters_data is None:
            parameters_data = []
        if not isinstance(parameters_data, list):
            raise ManifestError("resource.parameters must be a list if present")
        parameters = [Parameter.from_dict(p) for p in parameters_data]

        return Resource(
            name=name,
            resource_file=resource_file,
            deployment_targets=deployment_targets,
            deploy_method=method_enum,
            regions=regions,
            parameters=parameters,
        )


@dataclass
class Manifest:
    region: str
    version: date
    resources: list[Resource]

    @staticmethod
    def from_dict(data: dict, service_managed_perms: bool) -> "Manifest":
        for f in ["region", "version", "resources"]:
            if f not in data:
                raise ManifestError(f"manifest missing required field '{f}'")

        region = data["region"]
        version = data["version"]
        resources_data = data["resources"]

        if not isinstance(region, str):
            raise ManifestError("region must be a string")
        if not isinstance(version, date):
            raise ManifestError("version must be a date")
        if not isinstance(resources_data, list):
            raise ManifestError("resources must be a list")

        resources = [
            Resource.from_dict(r, service_managed_perms) for r in resources_data
        ]
        return Manifest(
            region=region,
            version=version,
            resources=resources,
        )


def load_manifest_from_path(path: Path, service_managed_perms: bool) -> Manifest:
    """Load and validate a Manifest from a file path containing YAML.

    Raises ManifestError on validation issues.
    """
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return Manifest.from_dict(data, service_managed_perms)
