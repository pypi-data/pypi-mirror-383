from __future__ import annotations

import dagster as dg

from dagster_ray._base.constants import DEFAULT_DEPLOYMENT_NAME


def get_dagster_tags(
    context: dg.InitResourceContext | dg.OpExecutionContext | dg.AssetExecutionContext,
    extra_tags: dict[str, str] | None = None,
) -> dict[str, str]:
    """
    Returns a dictionary with common Dagster tags.
    """
    assert context.dagster_run is not None
    assert context.dagster_run.step_keys_to_execute is not None

    labels: dict[str, str] = {
        "dagster/deployment": DEFAULT_DEPLOYMENT_NAME,  # TODO: this should come from extra_tags,
        **(extra_tags or {}),
    }

    if isinstance(context, dg.InitResourceContext):
        labels.update(
            **context.dagster_run.dagster_execution_info,
        )

        for resource_key, resource_def in context.all_resource_defs.items():
            if resource_def is context.resource_def:
                # inject the resource key used for this KubeRay resource
                # this enables e.g reusing the same `RayCluster` across Dagster steps that require it without recreating the cluster
                labels["dagster/resource-key"] = resource_key
    else:
        labels.update(
            **context.run.dagster_execution_info,
        )

    step_keys = context.dagster_run.step_keys_to_execute
    if step_keys is not None and len(step_keys) == 1:
        labels["dagster/step-key"] = step_keys[0]

    return labels
