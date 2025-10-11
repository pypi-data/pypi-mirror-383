import http

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.notebook_engine.client import NotebookEngineClient
from h2o_engine_manager.clients.notebook_engine.engine import NotebookEngine


# Actual resize cannot be tested in Skaffold env as Kind dont support volume expansion.
@pytest.mark.timeout(100)
def test_resize_storage_validation(
        notebook_engine_client_super_admin: NotebookEngineClient,
        notebook_engine_profile_p5,
        notebook_engine_image_i6,
):
    workspace_id = "default"
    engine_id = "resize-storage"

    try:
        engine = notebook_engine_client_super_admin.create_notebook_engine(
            parent=f"workspaces/{workspace_id}",
            notebook_engine=NotebookEngine(
                profile=notebook_engine_profile_p5.name,
                notebook_image=notebook_engine_image_i6.name,
                display_name="Notebook resize-storage",
            ),
            notebook_engine_id=engine_id,
        )

        assert engine.storage_bytes == notebook_engine_profile_p5.storage_bytes_constraint.default

        # Cannot exceed the maximum storage size.
        with pytest.raises(CustomApiException) as exc:
            notebook_engine_client_super_admin.resize_notebook_engine_storage(
                name=f"workspaces/{workspace_id}/notebookEngines/{engine_id}",
                new_storage="2000Gi"
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST

        # Cannot exceed the minimum storage size.
        with pytest.raises(CustomApiException) as exc:
            notebook_engine_client_super_admin.resize_notebook_engine_storage(
                name=f"workspaces/{workspace_id}/notebookEngines/{engine_id}",
                new_storage="1Mi"
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST

    finally:
        notebook_engine_client_super_admin.delete_notebook_engine(
            name=f"workspaces/{workspace_id}/notebookEngines/{engine_id}",
        )
