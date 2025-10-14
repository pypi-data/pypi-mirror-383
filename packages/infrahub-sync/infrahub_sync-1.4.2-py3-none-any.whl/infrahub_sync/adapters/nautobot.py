from __future__ import annotations

# pylint: disable=R0801
import os
from typing import TYPE_CHECKING, Any

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

import pynautobot
from diffsync import Adapter, DiffSyncModel

from infrahub_sync import (
    DiffSyncMixin,
    DiffSyncModelMixin,
    SchemaMappingModel,
    SyncAdapter,
    SyncConfig,
)

from .utils import get_value

if TYPE_CHECKING:
    from collections.abc import Mapping


class NautobotAdapter(DiffSyncMixin, Adapter):
    type = "Nautobot"

    def __init__(self, target: str, adapter: SyncAdapter, config: SyncConfig, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.target = target
        self.client = self._create_nautobot_client(adapter)
        self.config = config

    def _create_nautobot_client(self, adapter: SyncAdapter) -> pynautobot.api:
        settings = adapter.settings or {}
        url = os.environ.get("NAUTOBOT_ADDRESS") or os.environ.get("NAUTOBOT_URL") or settings.get("url")
        token = os.environ.get("NAUTOBOT_TOKEN") or settings.get("token")
        verify_ssl = settings.get("verify_ssl", True)

        if not url or not token:
            msg = "Both url and token must be specified!"
            raise ValueError(msg)

        client = pynautobot.api(url=url, token=token, threading=True, max_workers=5, retries=3, verify=verify_ssl)
        return client

    def model_loader(self, model_name: str, model: NautobotModel) -> None:
        """
        Load and process models using schema mapping filters and transformations.

        This method retrieves data from Nautobot, applies filters and transformations
        as specified in the schema mapping, and loads the processed data into the adapter.
        """
        # Retrieve schema mapping for this model
        for element in self.config.schema_mapping:
            if element.name != model_name:
                continue

            # Use the resource endpoint from the schema mapping
            app_name, resource_name = element.mapping.split(".")
            nautobot_app = getattr(self.client, app_name)
            nautobot_model = getattr(nautobot_app, resource_name)

            # Retrieve all objects (RecordSet)
            nodes = nautobot_model.all()

            # Transform the RecordSet into a list of Dict
            list_obj = []
            for node in nodes:
                list_obj.append(dict(node))

            total = len(list_obj)
            if self.config.source.name.title() == self.type.title():
                # Filter records
                filtered_objs = model.filter_records(records=list_obj, schema_mapping=element)
                print(f"{self.type}: Loading {len(filtered_objs)}/{total} {resource_name}")
                # Transform records
                transformed_objs = model.transform_records(records=filtered_objs, schema_mapping=element)
            else:
                print(f"{self.type}: Loading all {total} {resource_name}")
                transformed_objs = list_obj

            # Create model instances after filtering and transforming
            for obj in transformed_objs:
                data = self.nautobot_obj_to_diffsync(obj=obj, mapping=element, model=model)
                item = model(**data)
                self.add(item)

    def nautobot_obj_to_diffsync(self, obj: dict[str, Any], mapping: SchemaMappingModel, model: NautobotModel) -> dict:
        obj_id = obj.get("id")
        data: dict[str, Any] = {"local_id": str(obj_id)}

        for field in mapping.fields:  # pylint: disable=too-many-nested-blocks
            field_is_list = model.is_list(name=field.name)

            if field.static:
                data[field.name] = field.static
            elif not field_is_list and field.mapping and not field.reference:
                value = get_value(obj, field.mapping)
                if value is not None:
                    data[field.name] = value
            elif field_is_list and field.mapping and not field.reference:
                msg = "it's not supported yet to have an attribute of type list with a simple mapping"
                raise NotImplementedError(msg)

            elif field.mapping and field.reference:
                all_nodes_for_reference = self.store.get_all(model=field.reference)
                nodes = [item for item in all_nodes_for_reference]
                if not nodes and all_nodes_for_reference:
                    msg = (
                        f"Unable to get '{field.mapping}' with '{field.reference}' reference from store."
                        f" The available models are {self.store.get_all_model_names()}"
                    )
                    raise IndexError(msg)
                if not field_is_list:
                    if node := get_value(obj, field.mapping):
                        matching_nodes = []
                        node_id = node.get("id", None)
                        if node_id:
                            matching_nodes = [item for item in nodes if item.local_id == str(node_id)]
                            if len(matching_nodes) == 0:
                                # TODO: If the peer is a Node we are filtering, we could end up not finding it
                                print(f"Unable to locate the node {field.name} {node_id}")
                                continue
                            node = matching_nodes[0]
                            data[field.name] = node.get_unique_id()

                else:
                    data[field.name] = []
                    for node in get_value(obj, field.mapping):
                        if not node:
                            continue
                        node_id = node.get("id", None)
                        if not node_id and isinstance(node, tuple):
                            node_id = node[1] if node[0] == "id" else None
                            if not node_id:
                                continue
                        matching_nodes = [item for item in nodes if item.local_id == str(node_id)]
                        if len(matching_nodes) == 0:
                            # TODO: If the peer is a Node we are filtering, we could end up not finding it
                            print(f"Unable to locate the node {field.name} {node_id}")
                            continue
                        data[field.name].append(matching_nodes[0].get_unique_id())
                    data[field.name] = sorted(data[field.name])

        return data


class NautobotModel(DiffSyncModelMixin, DiffSyncModel):
    @classmethod
    def create(
        cls,
        adapter: Adapter,
        ids: Mapping[Any, Any],
        attrs: Mapping[Any, Any],
    ) -> Self | None:
        # TODO: To implement
        return super().create(adapter=adapter, ids=ids, attrs=attrs)

    def update(self, attrs: dict) -> Self | None:
        # TODO: To implement
        return super().update(attrs=attrs)
