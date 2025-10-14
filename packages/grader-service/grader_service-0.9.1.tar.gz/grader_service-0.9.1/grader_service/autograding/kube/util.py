# Copyright (c) 2022, TU Wien
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import copy
import hashlib
import os
from typing import Optional

from kubernetes import config
from kubernetes.client.models import (
    V1Container,
    V1EnvVar,
    V1ObjectMeta,
    V1Pod,
    V1PodSecurityContext,
    V1PodSpec,
    V1ResourceRequirements,
    V1SecurityContext,
    V1Toleration,
    V1Volume,
    V1VolumeMount,
)


def get_current_namespace():
    ns_path = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
    if os.path.exists(ns_path):
        with open(ns_path) as f:
            return f.read().strip()
    try:
        _, active_context = config.list_kube_config_contexts()
        return active_context["context"]["namespace"]
    except KeyError:
        return "default"


def generate_hashed_slug(slug, limit=63, hash_length=6):
    """
    Generate a unique name that's within a certain length limit

    Most k8s objects have a 63 char name limit. We wanna be able to compress
    larger names down to that if required, while still maintaining some
    amount of legibility about what the objects really are.

    If the length of the slug is shorter than the limit - hash_length, we just
    return slug directly. If not, we truncate the slug to (limit - hash_length)
    characters, hash the slug and append hash_length characters from the hash
    to the end of the truncated slug. This ensures that these names are always
    unique no matter what.
    """
    if len(slug) < (limit - hash_length):
        return slug

    slug_hash = hashlib.sha256(slug.encode("utf-8")).hexdigest()

    return "{prefix}-{hash}".format(
        prefix=slug[: limit - hash_length - 1], hash=slug_hash[:hash_length]
    ).lower()


def update_k8s_model(target, changes, logger=None, target_name=None, changes_name=None):
    """
    Takes a model instance such as V1PodSpec() and updates it with another
    model, which is allowed to be a dict or another model instance of the same
    type. The logger is used to warn if any truthy value in the target is is
    overridden. The target_name parameter can for example be "pod.spec", and
    changes_name parameter could be "extra_pod_config". These parameters allows
    the logger to write out something more meaningful to the user whenever
    something is about to become overridden.
    """
    model_type = type(target)
    if not hasattr(target, "attribute_map"):
        raise AttributeError(
            "Attribute 'target' ({}) must be an object (such as 'V1PodSpec') "
            "with an attribute 'attribute_map'.".format(model_type.__name__)
        )
    if not isinstance(changes, model_type) and not isinstance(changes, dict):
        raise AttributeError(
            "Attribute 'changes' ({}) must be an object of the same type "
            "as 'target' ({}) or a 'dict'.".format(type(changes).__name__, model_type.__name__)
        )

    changes_dict = _get_k8s_model_dict(model_type, changes)
    for key, value in changes_dict.items():
        if key not in target.attribute_map:
            raise ValueError(
                "The attribute 'changes' ({}) contained '{}' not modeled by '{}'.".format(
                    type(changes).__name__, key, model_type.__name__
                )
            )

        # If changes are passed as a dict, they will only have a few keys/value
        # pairs representing the specific changes.
        # If the changes parameter is a model instance on the other hand,
        # the changes parameter will have a lot of default values as well.
        # These default values, which are also falsy,
        # should not use to override the target's values.
        if isinstance(changes, dict) or value:
            if getattr(target, key):
                if logger and changes_name:
                    warning = (
                        "'{}.{}' current value: '{}' "
                        "is overridden with '{}', "
                        "which is the value of '{}.{}'.".format(
                            target_name, key, getattr(target, key), value, changes_name, key
                        )
                    )
                    logger.warning(warning)
            setattr(target, key, value)

    return target


def get_k8s_model(model_type, model_dict):
    """
    Returns an instance of type specified model_type from an model instance or
    represantative dictionary.
    """
    model_dict = copy.deepcopy(model_dict)

    if isinstance(model_dict, model_type):
        return model_dict
    elif isinstance(model_dict, dict):
        # convert the dictionaries camelCase keys to snake_case keys
        model_dict = _map_dict_keys_to_model_attributes(model_type, model_dict)
        # use the dictionary keys to initialize a model of given type
        return model_type(**model_dict)
    else:
        raise AttributeError(
            "Expected object of type 'dict' (or '{}') but got '{}'.".format(
                model_type.__name__, type(model_dict).__name__
            )
        )


def _get_k8s_model_dict(model_type, model):
    """
    Returns a dictionary representation of a provided model type
    """
    model = copy.deepcopy(model)

    if isinstance(model, model_type):
        return model.to_dict()
    elif isinstance(model, dict):
        return _map_dict_keys_to_model_attributes(model_type, model)
    else:
        raise AttributeError(
            "Expected object of type '{}' (or 'dict') but got '{}'.".format(
                model_type.__name__, type(model).__name__
            )
        )


def _map_dict_keys_to_model_attributes(model_type, model_dict):
    """
    Maps a dict's keys to the provided models attributes
    using its attribute_map attribute.
    This is (always?) the same as converting camelCase to snake_case.
    Note that the function will not influence nested object's keys.
    """

    new_dict = {}
    for key, value in model_dict.items():
        new_dict[_get_k8s_model_attribute(model_type, key)] = value

    return new_dict


def _get_k8s_model_attribute(model_type, field_name):
    """
    Takes a model type and a Kubernetes API resource field name (such as
    "serviceAccount") and returns a related attribute name (such as
    "service_account") to be used with  kubernetes.client.models objects. It is
    impossible to prove a negative but it seems like it is always a question of
    making camelCase to snake_case but by using the provided 'attribute_map' we
    also ensure that the fields actually exist.

    Example of V1PodSpec's attribute_map:
    {
        'active_deadline_seconds': 'activeDeadlineSeconds',
        'affinity': 'affinity',
        'automount_service_account_token': 'automountServiceAccountToken',
        'containers': 'containers',
        'dns_policy': 'dnsPolicy',
        'host_aliases': 'hostAliases',
        'host_ipc': 'hostIPC',
        'host_network': 'hostNetwork',
        'host_pid': 'hostPID',
        'hostname': 'hostname',
        'image_pull_secrets': 'imagePullSecrets',
        'init_containers': 'initContainers',
        'node_name': 'nodeName',
        'node_selector': 'nodeSelector',
        'priority': 'priority',
        'priority_class_name': 'priorityClassName',
        'restart_policy': 'restartPolicy',
        'scheduler_name': 'schedulerName',
        'security_context': 'securityContext',
        'service_account': 'serviceAccount',
        'service_account_name': 'serviceAccountName',
        'subdomain': 'subdomain',
        'termination_grace_period_seconds': 'terminationGracePeriodSeconds',
        'tolerations': 'tolerations',
        'volumes': 'volumes'
    }
    """
    # if we get "service_account", return
    if field_name in model_type.attribute_map:
        return field_name

    # if we get "serviceAccount", then return "service_account"
    for key, value in model_type.attribute_map.items():
        if value == field_name:
            return key
    else:
        raise ValueError(
            "'{}' did not have an attribute matching '{}'".format(model_type.__name__, field_name)
        )


def make_pod(
    name: str,
    cmd: list[str],
    env: list[V1EnvVar],
    image: str,
    image_pull_policy: str,
    image_pull_secrets: Optional[list] = None,
    working_dir: Optional[str] = None,
    volumes: Optional[list] = None,
    volume_mounts: Optional[list] = None,
    labels: Optional[dict] = None,
    annotations: Optional[dict] = None,
    node_selector: Optional[dict] = None,
    tolerations: Optional[list] = None,
    run_as_user: Optional[int] = None,
) -> V1Pod:
    """
    Creates a Kubernetes Pod specification (V1Pod) with the given parameters.

    Args:
        name (str): The name of the pod.
        cmd (list[str]): The command to run in the pod.
        image (str): The Docker image to use for the pod's container.
        image_pull_policy (str): The image pull policy.
        image_pull_secrets (Optional[list], default None): List of secrets to pull images from private registries.
        working_dir (Optional[str], default None): The working directory for the container.
        volumes (Optional[list], default None): List of volumes to attach to the pod.
        volume_mounts (Optional[list], default None): List of volume mounts for the container.
        labels (Optional[dict], default None): Labels to associate with the pod.
        annotations (Optional[dict], default None): Annotations to associate with the pod.
        node_selector (Optional[dict], default None): Node selectors to determine where the pod should be scheduled.
        tolerations (Optional[list], default None): Tolerations to apply for the pod.
        run_as_user (Optional[int], default None): The user ID under which the container should run.

    Returns:
        V1Pod: The Kubernetes Pod specification object.
    """
    pod = V1Pod()
    pod.kind = "Pod"
    pod.api_version = "v1"

    pod.metadata = V1ObjectMeta(
        name=name, labels=(labels or {}).copy(), annotations=(annotations or {}).copy()
    )

    pod.spec = V1PodSpec(
        containers=[],
        security_context=V1PodSecurityContext(),
        image_pull_secrets=image_pull_secrets,
        restart_policy="Never",
        node_selector=node_selector,
    )
    # TODO maybe get userid of jupyterhub user
    autograde_container = V1Container(
        name="autograde",
        image=image,
        working_dir=working_dir,
        args=cmd,
        env=env,
        image_pull_policy=image_pull_policy,
        resources=V1ResourceRequirements(),
        security_context=V1SecurityContext(run_as_user=run_as_user),
        volume_mounts=[get_k8s_model(V1VolumeMount, obj) for obj in (volume_mounts or [])],
    )

    pod.spec.containers.append(autograde_container)
    if tolerations:
        pod.spec.tolerations = [get_k8s_model(V1Toleration, obj) for obj in tolerations]
    if volumes:
        pod.spec.volumes = [get_k8s_model(V1Volume, obj) for obj in volumes]

    return pod
