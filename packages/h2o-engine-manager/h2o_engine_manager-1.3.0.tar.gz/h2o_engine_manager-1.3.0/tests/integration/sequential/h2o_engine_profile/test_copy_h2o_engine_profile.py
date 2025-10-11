import http
import re

import pytest

from h2o_engine_manager.clients.constraint.profile_constraint_duration import (
    ProfileConstraintDuration,
)
from h2o_engine_manager.clients.constraint.profile_constraint_numeric import (
    ProfileConstraintNumeric,
)
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.h2o_engine_profile.h2o_engine_profile import (
    H2OEngineProfile,
)
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_copy_h2o_engine_profile(
        h2o_engine_profile_client_super_admin,
        h2o_engine_profile_client,
        delete_all_h2o_engine_profiles_before_after,
):
    source = h2o_engine_profile_client_super_admin.create_h2o_engine_profile(
        parent=GLOBAL_WORKSPACE,
        h2o_engine_profile=(H2OEngineProfile(
            node_count_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0", maximum="10", cumulative_maximum="100"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="100", default="100"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="100s", default="200s"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="100s", default="200s", maximum="400s"),
            assigned_oidc_roles_enabled=True,
            assigned_oidc_roles=["admin"]
        )),
        h2o_engine_profile_id="p1",
    )

    # user cannot COPY profile in the global WS
    with pytest.raises(CustomApiException) as exc:
        h2o_engine_profile_client.copy_h2o_engine_profile(
            name="workspaces/global/h2oEngineProfiles/p1",
            parent="workspaces/global",
            h2o_engine_profile_id="p1-copy"
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN


    created = h2o_engine_profile_client_super_admin.copy_h2o_engine_profile(
        name="workspaces/global/h2oEngineProfiles/p1",
        parent="workspaces/global",
        h2o_engine_profile_id="p1-copy",
    )

    # Check that Get method returns correct data.
    assert created.node_count_constraint == ProfileConstraintNumeric(minimum="1", default="1")
    assert created.cpu_constraint == ProfileConstraintNumeric(minimum="1", default="1")
    assert created.gpu_constraint == ProfileConstraintNumeric(
        minimum="0", default="0", maximum="10", cumulative_maximum="100"
    )
    assert created.memory_bytes_constraint == ProfileConstraintNumeric(minimum="100", default="100")
    assert created.max_idle_duration_constraint == ProfileConstraintDuration(minimum="100s", default="200s")
    assert created.max_running_duration_constraint == ProfileConstraintDuration(
        minimum="100s", default="200s", maximum="400s"
    )
    assert created.name == "workspaces/global/h2oEngineProfiles/p1-copy"
    assert created.display_name == ""
    assert created.priority == 0
    assert created.enabled is True
    assert created.assigned_oidc_roles_enabled is True
    assert created.assigned_oidc_roles == ["admin"]
    assert created.max_running_engines is None
    assert created.yaml_pod_template_spec == ""
    assert created.yaml_gpu_tolerations == ""
    assert created.create_time.timestamp() > source.create_time.timestamp()
    assert created.update_time is None
    assert re.match(r"^users/.+$", created.creator)
    assert created.updater == ""
    assert created.creator_display_name == "test-super-admin"
    assert created.updater_display_name == ""
    assert created.gpu_resource_name == "nvidia.com/gpu"
