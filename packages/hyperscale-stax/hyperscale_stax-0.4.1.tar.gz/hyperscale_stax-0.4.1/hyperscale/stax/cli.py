import tempfile
import time
import zipfile
from pathlib import Path

import boto3
import cfnlint
import click
from botocore.exceptions import ClientError
from sigstore.errors import VerificationError

from hyperscale.stax.core import create_deployer
from hyperscale.stax.core import create_stack_deployer
from hyperscale.stax.manifest import DeployMethod
from hyperscale.stax.manifest import load_manifest_from_path
from hyperscale.stax.sigstore import verify_bundle_signature


@click.group()
@click.version_option(package_name="hyperscale.stax")
def main():
    """Deploy CloudFormation Stacks"""
    pass


@main.command(name="list")
@click.option(
    "-n", "--namespace", default="stax", help="A namespace for deployed resources"
)
def list_resources(namespace):
    """List all stack sets and stacks in the namespace"""
    cfn = boto3.client("cloudformation")

    # List stack sets
    stack_sets = _list_stack_sets(cfn, namespace)
    if stack_sets:
        click.echo("Stack Sets:")
        for stack_set in stack_sets:
            click.echo(f"  {stack_set['StackSetName']}")
            for instance in _list_stack_set_instances(cfn, stack_set["StackSetName"]):
                click.echo(f"    {instance['Account']} - {instance['Region']}")

    # List regular stacks
    stacks = _list_stacks(cfn, namespace)
    if stacks:
        if stack_sets:
            click.echo()  # Add spacing between sections
        click.echo("Stacks:")
        for stack in stacks:
            click.echo(f"  {stack['StackName']} - {stack['StackStatus']}")

    if not stack_sets and not stacks:
        click.echo(f"No resources found in namespace '{namespace}'")


def _get_stack_set(cfn, stack_set_name):
    try:
        details = cfn.describe_stack_set(CallAs="SELF", StackSetName=stack_set_name)[
            "StackSet"
        ]
        return details
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code != "StackSetNotFoundException":
            raise
    raise click.ClickException(f"Stack set not found: {stack_set_name}")


def _delete_stack_set(cfn, stack_set_name):
    details = _get_stack_set(cfn, stack_set_name)
    if details["OrganizationalUnitIds"]:
        cfn.delete_stack_instances(
            StackSetName=stack_set_name,
            DeploymentTargets={
                "OrganizationalUnitIds": details["OrganizationalUnitIds"],
            },
            Regions=details["Regions"],
            RetainStacks=False,
            CallAs="SELF",
        )

    attempt = 0
    success = False
    while attempt < 30 and not success:
        try:
            cfn.delete_stack_set(StackSetName=stack_set_name, CallAs="SELF")
            success = True
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code != "OperationInProgressException":
                raise
            attempt += 1
            click.echo("Waiting for stack set operation to complete...")
            time.sleep(10)
    if not success:
        raise click.ClickException(
            "Timed out waiting for stack set operation to complete - stacks not updated"
        )


def _list_stack_sets(cfn, namespace):
    result = []
    paginator = cfn.get_paginator("list_stack_sets")
    for page in paginator.paginate(CallAs="SELF", Status="ACTIVE"):
        for stack_set in page["Summaries"]:
            details = _get_stack_set(cfn, stack_set["StackSetName"])
            if details.get("Tags"):
                for tag in details["Tags"]:
                    if tag["Key"] == "stax:namespace" and tag["Value"] == namespace:
                        result.append(stack_set)
    return result


def _list_stack_set_instances(cfn, stack_set_name):
    paginator = cfn.get_paginator("list_stack_instances")
    for page in paginator.paginate(StackSetName=stack_set_name, CallAs="SELF"):
        yield from page["Summaries"]


def _list_stacks(cfn, namespace):
    result = []
    paginator = cfn.get_paginator("list_stacks")
    for page in paginator.paginate(
        StackStatusFilter=[
            "CREATE_COMPLETE",
            "UPDATE_COMPLETE",
            "UPDATE_ROLLBACK_COMPLETE",
            "IMPORT_COMPLETE",
        ]
    ):
        for stack in page["StackSummaries"]:
            # Check if stack has the namespace tag
            try:
                stack_details = cfn.describe_stacks(StackName=stack["StackName"])[
                    "Stacks"
                ][0]
                if stack_details.get("Tags"):
                    for tag in stack_details["Tags"]:
                        if tag["Key"] == "stax:namespace" and tag["Value"] == namespace:
                            result.append(stack)
                            break
            except ClientError:
                # Skip stacks that can't be described
                continue
    return result


def _delete_stack(cfn, stack_name):
    try:
        cfn.delete_stack(StackName=stack_name)
        click.echo(f"Deleting stack: {stack_name}")
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code != "ValidationError":
            raise
        click.echo(f"Stack not found: {stack_name}")


@main.command(name="delete")
@click.argument("resource_name")
@click.option(
    "-t",
    "--type",
    type=click.Choice(["stack_set", "stack"]),
    default="stack_set",
    help="Type of resource to delete",
)
def delete_resource(resource_name, type):
    """Delete a stack set or stack"""
    cfn = boto3.client("cloudformation")
    if type == "stack_set":
        _delete_stack_set(cfn, resource_name)
    elif type == "stack":
        _delete_stack(cfn, resource_name)


@main.command()
@click.option(
    "-n", "--namespace", default="stax", help="A namespace for deployed resources"
)
@click.option(
    "-s",
    "--sigstore-bundle",
    default=None,
    required=False,
    type=click.Path(exists=True),
    help="Path to a Sigstore bundle to verify",
)
@click.option(
    "-i", "--oidc-identity", default=None, help="OIDC identity to verify against"
)
@click.option("-r", "--oidc-issuer", default=None, help="OIDC issuer to verify against")
@click.option(
    "-a",
    "--admin-role-arn",
    default=None,
    help="The role ARN for a custom CloudFormation administrator role",
)
@click.option(
    "-e",
    "--execution-role-name",
    default=None,
    help="The role name for the execution role deployed in each target account",
)
@click.argument("archive", required=True, type=click.Path(exists=True))
def deploy(
    archive,
    namespace,
    sigstore_bundle,
    oidc_identity,
    oidc_issuer,
    admin_role_arn,
    execution_role_name,
):
    """Deploy the archive"""
    archive_path = Path(archive)

    if archive_path.suffix.lower() != ".zip":
        raise click.BadParameter("archive must be a .zip file", param_hint=["archive"])

    if not zipfile.is_zipfile(archive_path):
        raise click.BadParameter(
            "archive is not a valid ZIP archive", param_hint=["archive"]
        )

    if any([sigstore_bundle, oidc_identity, oidc_issuer]) and not all(
        [sigstore_bundle, oidc_identity, oidc_issuer]
    ):
        raise click.BadParameter(
            "must provide all of sigstore-bundle, oidc-identity, oidc-issuer "
            "or none of them",
            param_hint=["sigstore-bundle", "oidc-identity", "oidc-issuer"],
        )

    if any([execution_role_name, admin_role_arn]) and not all(
        [execution_role_name, admin_role_arn]
    ):
        raise click.BadParameter(
            "must provide both of admin-role-arn and execution-role-name "
            "or none of them",
            param_hint=["admin-role-arn", "execution-role-name"],
        )

    if sigstore_bundle:
        try:
            verify_bundle_signature(
                archive_path, sigstore_bundle, oidc_identity, oidc_issuer
            )
        except VerificationError as e:
            raise click.ClickException(f"Signature verification failed: {e}") from e

    with tempfile.TemporaryDirectory(prefix="stax_archive_") as tmpdir:
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(tmpdir)

        tmp_path = Path(tmpdir)
        manifest_path = tmp_path / "manifest.yaml"
        if not manifest_path.exists():
            raise click.ClickException("manifest.yaml not found at bundle root")

        service_managed_perms = admin_role_arn is None
        manifest = load_manifest_from_path(manifest_path, service_managed_perms)

        templates_dir = tmp_path / "templates"
        if templates_dir.exists() and templates_dir.is_dir():
            template_files = sorted(templates_dir.glob("*.yaml"))
            if template_files:
                lint_errors = _run_cfn_lint(template_files)
                if lint_errors:
                    raise click.ClickException(
                        "cfn-lint found issues:\n" + "\n".join(lint_errors)
                    )
            else:
                raise click.ClickException("No templates found")
        else:
            raise click.ClickException("No templates found")
        cfn = boto3.client("cloudformation", region_name=manifest.region)

        for resource in manifest.resources:
            if resource.deploy_method == DeployMethod.STACK_SET:
                _deploy_stack_set(
                    cfn,
                    tmp_path,
                    manifest.region,
                    resource,
                    namespace,
                    admin_role_arn,
                    execution_role_name,
                )
            elif resource.deploy_method == DeployMethod.STACK:
                _deploy_stack(
                    cfn,
                    tmp_path,
                    manifest.region,
                    resource,
                    namespace,
                )

        # delete orphaned stack sets
        stack_sets = _list_stack_sets(cfn, namespace)
        for stack_set in stack_sets:
            if stack_set["StackSetName"] not in [
                f"{namespace}-{resource.name}"
                for resource in manifest.resources
                if resource.deploy_method == DeployMethod.STACK_SET
            ]:
                click.echo(f"Deleting orphaned stack set {stack_set['StackSetName']}")
                _delete_stack_set(cfn, stack_set["StackSetName"])

        # delete orphaned stacks
        stacks = _list_stacks(cfn, namespace)
        for stack in stacks:
            if stack["StackName"] not in [
                f"{namespace}-{resource.name}"
                for resource in manifest.resources
                if resource.deploy_method == DeployMethod.STACK
            ]:
                click.echo(f"Deleting orphaned stack {stack['StackName']}")
                _delete_stack(cfn, stack["StackName"])


if __name__ == "__main__":
    main()


def _stack_set_exists(cfn, stack_set_name):
    try:
        cfn.describe_stack_set(StackSetName=stack_set_name, CallAs="SELF")
        return True
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code != "StackSetNotFoundException":
            raise
    return False


def _deploy_stack_set(
    cfn,
    bundle_root: Path,
    default_region: str,
    resource,
    namespace: str,
    admin_role_arn: str | None,
    execution_role_name: str | None,
) -> None:
    stack_set_name = f"{namespace}-{resource.name}"
    template_path = bundle_root / resource.resource_file
    if not template_path.exists():
        raise click.ClickException(
            f"Template not found for resource '{resource.name}': {template_path}"
        )

    with template_path.open("r", encoding="utf-8") as fh:
        template_body = fh.read()

    parameters = [
        {
            "ParameterKey": p.parameter_key,
            "ParameterValue": p.parameter_value,
        }
        for p in getattr(resource, "parameters", [])
    ]

    deployer = create_deployer(cfn, admin_role_arn, execution_role_name, namespace)
    regions = resource.regions or [default_region]

    if _stack_set_exists(cfn, stack_set_name):
        click.echo(f"Existing stack set found: {stack_set_name} - updating")
        try:
            deployer.update_stack_set(
                stack_set_name,
                template_body,
                parameters,
                resource.deployment_targets,
                regions,
            )
        except ClientError as exc:
            if (
                exc.response.get("Error", {}).get("Code")
                != "StackInstanceNotFoundException"
            ):
                raise

            click.echo(
                "Updating a stack with no stack instances - ignoring and "
                "proceeding to create stack instances"
            )

    else:
        click.echo(f"No existing stack set found: {stack_set_name} - creating")
        deployer.create_stack_set(stack_set_name, template_body, parameters)

    click.echo(f"Deploying stack set instances: {stack_set_name}")
    attempt = 0
    success = False
    while attempt < 30 and not success:
        try:
            deployer.create_stack_instances(
                stack_set_name, resource.deployment_targets, regions
            )
            success = True
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code != "OperationInProgressException":
                raise
            attempt += 1
            click.echo("Waiting for stack set operation to complete...")
            time.sleep(10)
    if not success:
        raise click.ClickException(
            "Timed out waiting for stack set operation to complete - stacks not updated"
        )


def _stack_exists(cfn, stack_name):
    try:
        cfn.describe_stacks(StackName=stack_name)
        return True
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code != "ValidationError":
            raise
    return False


def _deploy_stack(
    cfn,
    bundle_root: Path,
    default_region: str,
    resource,
    namespace: str,
) -> None:
    stack_name = f"{namespace}-{resource.name}"
    template_path = bundle_root / resource.resource_file
    if not template_path.exists():
        raise click.ClickException(
            f"Template not found for resource '{resource.name}': {template_path}"
        )

    with template_path.open("r", encoding="utf-8") as fh:
        template_body = fh.read()

    parameters = [
        {
            "ParameterKey": p.parameter_key,
            "ParameterValue": p.parameter_value,
        }
        for p in getattr(resource, "parameters", [])
    ]

    stack_deployer = create_stack_deployer(cfn, namespace)
    regions = resource.regions or [default_region]

    # For stack deployment, we deploy to each region specified
    for region in regions:
        if region != default_region:
            # Create a new CloudFormation client for each region
            cfn_region = boto3.client("cloudformation", region_name=region)
            stack_deployer_region = create_stack_deployer(cfn_region, namespace)
        else:
            stack_deployer_region = stack_deployer

        cfn_client = cfn_region if region != default_region else cfn
        if _stack_exists(cfn_client, stack_name):
            click.echo(f"Existing stack found: {stack_name} in {region} - updating")
            try:
                stack_deployer_region.update_stack(
                    stack_name, template_body, parameters, region
                )
            except ClientError as exc:
                if exc.response.get("Error", {}).get("Code") == "ValidationError":
                    click.echo(
                        f"No changes to deploy for stack {stack_name} in {region}"
                    )
                else:
                    raise
        else:
            click.echo(f"No existing stack found: {stack_name} in {region} - creating")
            stack_deployer_region.create_stack(
                stack_name, template_body, parameters, region
            )


def _run_cfn_lint(template_files: list[Path]) -> list[str]:
    errors: list = []

    for path in template_files:
        matches = cfnlint.lint_file(path)
        errors.extend(matches)
    return errors
