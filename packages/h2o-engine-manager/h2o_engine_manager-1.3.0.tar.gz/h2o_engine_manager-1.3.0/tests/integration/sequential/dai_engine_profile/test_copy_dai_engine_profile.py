import http
import re
import time

import pytest

from h2o_engine_manager.clients.constraint.profile_constraint_duration import (
    ProfileConstraintDuration,
)
from h2o_engine_manager.clients.constraint.profile_constraint_numeric import (
    ProfileConstraintNumeric,
)
from h2o_engine_manager.clients.dai_engine_profile.config_editability import (
    ConfigEditability,
)
from h2o_engine_manager.clients.dai_engine_profile.dai_engine_profile import (
    DAIEngineProfile,
)
from h2o_engine_manager.clients.exception import CustomApiException
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_copy_dai_engine_profile(
        dai_engine_profile_client_super_admin,
        dai_engine_profile_client,
        delete_all_dai_engine_profiles_before_after,
):
    original = dai_engine_profile_client_super_admin.create_dai_engine_profile(
        parent=GLOBAL_WORKSPACE,
        dai_engine_profile=(DAIEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0", maximum="10", cumulative_maximum="100"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="100", default="100"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="100", default="100"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="100s", default="200s"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="100s", default="200s", maximum="400s"),
            config_editability=ConfigEditability.CONFIG_EDITABILITY_FULL,
            assigned_oidc_roles_enabled=True,
            assigned_oidc_roles=["admin"]
        )),
        dai_engine_profile_id="p1",
    )

    # regular user cannot copy profile
    with pytest.raises(CustomApiException) as exc:
        dai_engine_profile_client.copy_dai_engine_profile(
            name=original.name,
            parent=GLOBAL_WORKSPACE,
            dai_engine_profile_id="p1-copy",
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN

    # super-admin can copy profile
    created = dai_engine_profile_client_super_admin.copy_dai_engine_profile(
        name=original.name,
        parent=GLOBAL_WORKSPACE,
        dai_engine_profile_id="p1-copy",
    )
    assert created.cpu_constraint == ProfileConstraintNumeric(minimum="1", default="1")
    assert created.gpu_constraint == ProfileConstraintNumeric(
        minimum="0", default="0", maximum="10", cumulative_maximum="100"
    )
    assert created.memory_bytes_constraint == ProfileConstraintNumeric(minimum="100", default="100")
    assert created.storage_bytes_constraint == ProfileConstraintNumeric(minimum="100", default="100")
    assert created.max_idle_duration_constraint == ProfileConstraintDuration(minimum="100s", default="200s")
    assert created.max_running_duration_constraint == ProfileConstraintDuration(
        minimum="100s", default="200s", maximum="400s"
    )
    assert created.config_editability == ConfigEditability.CONFIG_EDITABILITY_FULL
    assert created.name == "workspaces/global/daiEngineProfiles/p1-copy"
    assert created.display_name == ""
    assert created.priority == 0
    assert created.enabled is True
    assert created.assigned_oidc_roles_enabled is True
    assert created.assigned_oidc_roles == ["admin"]
    assert created.max_running_engines is None
    assert created.max_non_interaction_duration is None
    assert created.max_unused_duration is None
    assert created.configuration_override == {}
    assert created.base_configuration == {}
    assert created.yaml_pod_template_spec == ""
    assert created.yaml_gpu_tolerations == ""
    assert created.triton_enabled is False
    assert created.create_time.timestamp() > original.create_time.timestamp()
    assert created.update_time is None
    assert re.match(r"^users/.+$", created.creator)
    assert created.updater == ""
    assert created.creator_display_name == "test-super-admin"
    assert created.updater_display_name == ""
    assert created.gpu_resource_name == "nvidia.com/gpu"
    assert created.data_directory_storage_class == ""

