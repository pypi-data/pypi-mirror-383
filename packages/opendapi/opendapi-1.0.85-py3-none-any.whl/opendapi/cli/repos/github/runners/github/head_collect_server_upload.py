"""
CLI for collecting dapi file information at the head commit,
loading the base collected dapi file information,
analyzing them, uploading the required information to the DAPI server,
but not starting the server driven CICD.

This command is invoked in a github CI runner for a github repo for a specific runtime:
`opendapi github github head-collect-server-upload`
"""

# pylint: disable=duplicate-code

import click

from opendapi.cli.common import get_opendapi_config_from_root
from opendapi.cli.context_agnostic import (
    cicd_get_s3_upload_data,
    cicd_persist_files,
    collect_collected_files,
    load_locally_persisted_collected_files,
    server_sync_minimal_schemas,
)
from opendapi.cli.options import (
    CURRENTLY_CHECKED_OUT_COMMIT_SHA_PARAM_NAME_WITH_OPTION,
    OPENDAPI_CONFIG_PARAM_NAME_WITH_OPTION,
    SKIP_DBT_INTEGRATION_HEAD_GENERATION_OPTION,
    SKIP_RUNTIME_INTEGRATION_HEAD_GENERATION_OPTION,
    cicd_param_options,
    dapi_server_options,
    dev_options,
    generation_options,
    git_options,
    opendapi_run_options,
    runtime_options,
    schema_integration_options,
)
from opendapi.cli.repos.github.options import repo_options
from opendapi.cli.repos.github.runners.github.options import (
    construct_change_trigger_event,
    runner_options,
)
from opendapi.defs import CommitType


@click.command()
# common options
@dapi_server_options
@schema_integration_options
@dev_options
@generation_options
@opendapi_run_options
@runtime_options
@git_options
@cicd_param_options
# github repo options
@repo_options
# github repo github runner options
@runner_options
def cli(**kwargs):
    """
    CLI for collecting dapi file information at the head commit,
    loading the base collected dapi file information,
    analyzing them, uploading the required information to the DAPI server,
    but not starting the server driven CICD.

        This command is invoked in a github CI runner for a github repo for a specific runtime:
        `opendapi github github head-collect-server-upload`
    """

    runtime_skip_generation_at_head = kwargs[
        SKIP_RUNTIME_INTEGRATION_HEAD_GENERATION_OPTION.name
    ]
    dbt_skip_generation_at_head = kwargs[
        SKIP_DBT_INTEGRATION_HEAD_GENERATION_OPTION.name
    ]

    runtime = kwargs["runtime"]
    cicd_location_id = kwargs["cicd_location_id"]
    change_trigger_event = construct_change_trigger_event(kwargs)
    opendapi_config = kwargs.get(
        OPENDAPI_CONFIG_PARAM_NAME_WITH_OPTION.name
    ) or get_opendapi_config_from_root(
        local_spec_path=kwargs.get("local_spec_path"),
        validate_config=True,
    )
    opendapi_config.assert_runtime_exists(runtime)
    # for head collect we default to True if not set (None)
    currently_checked_out_commit_sha = kwargs.get(
        CURRENTLY_CHECKED_OUT_COMMIT_SHA_PARAM_NAME_WITH_OPTION.name
    )
    if (
        currently_checked_out_commit_sha
        and currently_checked_out_commit_sha != change_trigger_event.after_change_sha
    ):
        raise click.ClickException(
            "The currently checked out commit SHA does not match the after change SHA"
        )

    head_collected_files = collect_collected_files(
        opendapi_config,
        change_trigger_event=change_trigger_event,
        commit_type=CommitType.HEAD,
        runtime_skip_generation=runtime_skip_generation_at_head,
        dbt_skip_generation=dbt_skip_generation_at_head,
        minimal_schemas=server_sync_minimal_schemas(),
        runtime=runtime,
        commit_already_checked_out=currently_checked_out_commit_sha
        == change_trigger_event.after_change_sha,
        kwargs=kwargs,
    )
    base_collected_files = load_locally_persisted_collected_files(
        opendapi_config,
        CommitType.BASE,
        runtime,
    )

    s3_upload_data = cicd_get_s3_upload_data(
        cicd_location_id,
        change_trigger_event,
        kwargs,
    )
    cicd_persist_files(
        base_collected_files,
        head_collected_files,
        change_trigger_event,
        opendapi_config,
        s3_upload_data,
        runtime,
        kwargs,
    )
