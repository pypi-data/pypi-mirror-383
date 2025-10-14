from dataclasses import dataclass
from typing import Protocol

from botocore.client import BaseClient


class Deployer(Protocol):
    def create_stack_set(self, stack_set_name, template_body, parameters): ...
    def update_stack_set(
        self, stack_set_name, template_body, parameters, deployment_targets, regions
    ): ...
    def create_stack_instances(self, stack_set_name, deployment_targets, regions): ...


class StackDeployer(Protocol):
    def create_stack(self, stack_name, template_body, parameters, region): ...
    def update_stack(self, stack_name, template_body, parameters, region): ...


@dataclass
class SelfManagedPermissionsDeployer:
    cfn: BaseClient
    namespace: str
    admin_role_arn: str
    execution_role_name: str

    def create_stack_set(self, stack_set_name, template_body, parameters):
        self.cfn.create_stack_set(
            StackSetName=stack_set_name,
            TemplateBody=template_body,
            Parameters=parameters,
            AdministrationRoleARN=self.admin_role_arn,
            ExecutionRoleName=self.execution_role_name,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            PermissionModel="SELF_MANAGED",
            CallAs="SELF",
            Tags=[
                {"Key": "stax:created-by", "Value": "stax"},
                {"Key": "stax:namespace", "Value": self.namespace},
            ],
        )

    def update_stack_set(
        self,
        stack_set_name,
        template_body,
        parameters,
        deployment_targets,
        regions,
    ):
        self.cfn.update_stack_set(
            StackSetName=stack_set_name,
            TemplateBody=template_body,
            Parameters=parameters,
            AdministrationRoleARN=self.admin_role_arn,
            ExecutionRoleName=self.execution_role_name,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            CallAs="SELF",
            Accounts=deployment_targets.accounts,
            Regions=regions,
        )

    def create_stack_instances(self, stack_set_name, deployment_targets, regions):
        self.cfn.create_stack_instances(
            StackSetName=stack_set_name,
            Accounts=deployment_targets.accounts,
            Regions=regions,
            CallAs="SELF",
            OperationPreferences={
                "FailureTolerancePercentage": 30,
                "MaxConcurrentPercentage": 100,
                "RegionConcurrencyType": "SEQUENTIAL",
            },
        )


@dataclass
class ServiceManagedPermissionsDeployer:
    cfn: BaseClient
    namespace: str

    def create_stack_set(self, stack_set_name, template_body, parameters):
        self.cfn.create_stack_set(
            StackSetName=stack_set_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            PermissionModel="SERVICE_MANAGED",
            AutoDeployment={
                "Enabled": True,
                "RetainStacksOnAccountRemoval": False,
            },
            CallAs="SELF",
            Tags=[
                {"Key": "stax:created-by", "Value": "stax"},
                {"Key": "stax:namespace", "Value": self.namespace},
            ],
        )

    def update_stack_set(
        self, stack_set_name, template_body, parameters, deployment_targets, regions
    ):
        self.cfn.update_stack_set(
            StackSetName=stack_set_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            CallAs="SELF",
        )

    def create_stack_instances(self, stack_set_name, deployment_targets, regions):
        self.cfn.create_stack_instances(
            StackSetName=stack_set_name,
            DeploymentTargets=self.__get_target_spec(deployment_targets),
            Regions=regions,
            CallAs="SELF",
            OperationPreferences={
                "FailureTolerancePercentage": 30,
                "MaxConcurrentPercentage": 100,
                "RegionConcurrencyType": "SEQUENTIAL",
            },
        )

    def __get_target_spec(self, targets):
        target_spec = {}
        if targets.organizational_units:
            target_spec["OrganizationalUnitIds"] = targets.organizational_units
        if targets.accounts:
            # Uggh this API is horrible. Can't just specify accounts, despite what the
            # API docs say. Need to specify an OU the account ID is in, then use the
            # INTERSECTION filter type and then specify the account IDs.
            target_spec["Accounts"] = targets.accounts
            target_spec["AccountFilterType"] = "INTERSECTION"
            target_spec["OrganizationalUnitIds"] = targets.organizational_units
        return target_spec


@dataclass
class RegularStackDeployer:
    cfn: BaseClient
    namespace: str

    def create_stack(self, stack_name, template_body, parameters, region):
        self.cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            Tags=[
                {"Key": "stax:created-by", "Value": "stax"},
                {"Key": "stax:namespace", "Value": self.namespace},
            ],
        )

    def update_stack(self, stack_name, template_body, parameters, region):
        self.cfn.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
        )


def create_deployer(cfn, admin_role_arn, execution_role_name, namespace) -> Deployer:
    if admin_role_arn and execution_role_name:
        return SelfManagedPermissionsDeployer(
            cfn=cfn,
            admin_role_arn=admin_role_arn,
            execution_role_name=execution_role_name,
            namespace=namespace,
        )
    else:
        return ServiceManagedPermissionsDeployer(cfn, namespace)


def create_stack_deployer(cfn, namespace) -> StackDeployer:
    return RegularStackDeployer(cfn=cfn, namespace=namespace)
