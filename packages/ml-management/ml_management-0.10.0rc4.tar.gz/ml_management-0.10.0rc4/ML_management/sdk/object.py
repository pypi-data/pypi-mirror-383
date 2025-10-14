from typing import Literal, Optional, Union

from sgqlc.operation import Operation

from ML_management.graphql.schema import (
    DatasetLoaderInfo,
    DatasetLoaderVersionInfo,
    ExecutorInfo,
    ExecutorVersionInfo,
    ModelInfo,
    ModelVersionInfo,
    UpdateObjectForm,
    UpdateObjectVersionForm,
    schema,
)
from ML_management.graphql.send_graphql_request import send_graphql_request
from ML_management.mlmanagement.model_type import ModelType
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.sdk.sdk import _entity

_object_map = {
    ModelType.MODEL: ModelInfo,
    ModelType.DATASET_LOADER: DatasetLoaderInfo,
    ModelType.EXECUTOR: ExecutorInfo,
}

_object_version_map = {
    ModelType.MODEL: ModelVersionInfo,
    ModelType.DATASET_LOADER: DatasetLoaderVersionInfo,
    ModelType.EXECUTOR: ExecutorVersionInfo,
}


def set_object_tags(
    aggr_id: int,
    model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType],
    key: str,
    values: list[str],
) -> Union[ModelInfo, DatasetLoaderInfo, ExecutorInfo]:
    """
    Set object tags.

    Parameters
    ----------
    aggr_id: int
        Id of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    key: str
        Key tag.
    values: list[str]
        Value tags.

    Returns
    -------
    ModelInfo|DatasetLoaderInfo|ExecutorInfo
        Instance with meta information.
    """
    model_type = ModelType(model_type)
    op = Operation(schema.Mutation)
    set_tag = op.set_object_tags(aggr_id=aggr_id, key=key, values=values, model_type=model_type.name).__as__(
        _object_map[model_type]
    )
    _entity(set_tag)
    object_tags = send_graphql_request(op=op, json_response=False).set_object_tags
    return object_tags


def reset_object_tags(
    aggr_id: int,
    model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType],
    key: str,
    values: list[str],
    new_key: Optional[str] = None,
) -> Union[ModelInfo, DatasetLoaderInfo, ExecutorInfo]:
    """
    Reset object tags.

    Parameters
    ----------
    aggr_id: int
        Id of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    key: str
        Key tag.
    values: list[str]
        Value tag.
    new_key: Optional[str] = None
        New key of a tag.


    Returns
    -------
    ModelInfo|DatasetLoaderInfo|ExecutorInfo
        Instance with meta information.
    """
    model_type = ModelType(model_type)
    op = Operation(schema.Mutation)
    set_tag = op.reset_object_tags(
        aggr_id=aggr_id, key=key, values=values, new_key=new_key, model_type=model_type.name
    ).__as__(_object_map[model_type])
    _entity(set_tag)
    object_tags = send_graphql_request(op=op, json_response=False).reset_object_tags
    return object_tags


def delete_object_tag(
    aggr_id: int,
    model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType],
    key: str,
    value: Optional[str] = None,
) -> Union[ModelInfo, DatasetLoaderInfo, ExecutorInfo]:
    """
    Delete object tag.

    Parameters
    ----------
    aggr_id: int
        Id of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    key: str
        Key tag.
    value: Optional[str]=None
        value tag.
    Returns
    -------
    ModelInfo|DatasetLoaderInfo|ExecutorInfo
        Instance with meta information.
    """
    model_type = ModelType(model_type)
    op = Operation(schema.Mutation)
    delete_tag = op.delete_object_tag(aggr_id=aggr_id, key=key, value=value, model_type=model_type.name).__as__(
        _object_map[model_type]
    )
    _entity(delete_tag)
    object_tag = send_graphql_request(op=op, json_response=False).delete_object_tag
    return object_tag


def set_object_description(
    aggr_id: int, model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType], description: str
) -> Union[ModelInfo, DatasetLoaderInfo, ExecutorInfo]:
    """
    Set object description.

    Parameters
    ----------
    aggr_id: int
        Id of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    description: str
        Description model.

    Returns
    -------
    ModelInfo|DatasetLoaderInfo|ExecutorInfo
        Instance with meta information.
    """
    model_type = ModelType(model_type)
    op = Operation(schema.Mutation)
    set_description = op.update_object(
        aggr_id=aggr_id,
        update_object_form=UpdateObjectForm(new_description=description),
        model_type=model_type.name,
    ).__as__(_object_map[model_type])
    _entity(set_description)

    update_object = send_graphql_request(op=op, json_response=False).update_object
    return update_object


def set_object_visibility(
    aggr_id: int,
    model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType],
    visibility: Union[Literal["private", "public"], VisibilityOptions],
) -> Union[ModelInfo, DatasetLoaderInfo, ExecutorInfo]:
    """
    Set object visibility.

    Parameters
    ----------
    aggr_id: int
        Id of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        visibility model.

    Returns
    -------
    ModelInfo|DatasetLoaderInfo|ExecutorInfo
        Instance with meta information.
    """
    model_type = ModelType(model_type)

    op = Operation(schema.Mutation)
    set_visibility = op.update_object(
        aggr_id=aggr_id,
        model_type=model_type.name,
        update_object_form=UpdateObjectForm(new_visibility=VisibilityOptions(visibility).name),
    ).__as__(_object_map[model_type])
    _entity(set_visibility)

    update_object = send_graphql_request(op=op, json_response=False).update_object
    return update_object


def rename_object(
    aggr_id: int,
    model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType],
    new_name: str,
) -> Union[ModelInfo, DatasetLoaderInfo, ExecutorInfo]:
    """
    Rename object.

    Parameters
    ----------
    aggr_id: int
        Id of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    new_name: str
        new_name object.

    Returns
    -------
    ModelInfo|DatasetLoaderInfo|ExecutorInfo
        Instance with meta information.
    """
    model_type = ModelType(model_type)

    op = Operation(schema.Mutation)
    set_visibility = op.update_object(
        aggr_id=aggr_id,
        model_type=model_type.name,
        update_object_form=UpdateObjectForm(new_name=new_name),
    ).__as__(_object_map[model_type])
    _entity(set_visibility)

    update_object = send_graphql_request(op=op, json_response=False).update_object
    return update_object


def set_object_version_description(
    aggr_id: int,
    version: int,
    model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType],
    description: str,
) -> Union[ModelVersionInfo, ExecutorVersionInfo, DatasetLoaderVersionInfo]:
    """
    Set object version description.

    Parameters
    ----------
    aggr_id: int
        Id of the object.
    version: int
        Version of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER

    description: str
        Description model version.

    Returns
    -------
    Union[ ModelVersionInfo , ExecutorVersionInfo , DatasetLoaderVersionInfo]:
        Instance with meta information.
    """
    model_type = ModelType(model_type)

    op = Operation(schema.Mutation)
    choice = schema.ObjectIdVersionInput(aggr_id=aggr_id, version=version)
    set_description = op.update_object_version(
        object_version=choice,
        update_object_version_form=UpdateObjectVersionForm(new_description=description),
        model_type=model_type.name,
    ).__as__(_object_version_map[model_type])
    set_description.name()
    set_description.version()
    set_description.description()

    update_object = send_graphql_request(op=op, json_response=False).update_object_version
    return update_object


def set_object_version_visibility(
    aggr_id: int,
    version: int,
    model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType],
    visibility: Union[Literal["private", "public"], VisibilityOptions],
) -> Union[ModelVersionInfo, ExecutorVersionInfo, DatasetLoaderVersionInfo]:
    """
    Set object version visibility.

    Parameters
    ----------
    aggr_id: int
        Id of the object.
    version: int
        Version of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    visibility: Union[Literal['private', 'public'], VisibilityOptions]
        visibility model version.

    Returns
    -------
    Union[ ModelVersionInfo , ExecutorVersionInfo , DatasetLoaderVersionInfo]
        Instance with meta information.
    """
    model_type = ModelType(model_type)

    op = Operation(schema.Mutation)
    choice = schema.ObjectIdVersionInput(aggr_id=aggr_id, version=version)
    set_visibility = op.update_object_version(
        object_version=choice,
        update_object_version_form=UpdateObjectVersionForm(new_visibility=VisibilityOptions(visibility).name),
        model_type=model_type.name,
    ).__as__(_object_version_map[model_type])
    set_visibility.name()
    set_visibility.version()
    set_visibility.visibility()

    model = send_graphql_request(op=op, json_response=False).update_object_version
    return model


def set_object_version_tags(
    aggr_id: int,
    version: int,
    model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType],
    key: str,
    values: list[str],
) -> Union[ModelVersionInfo, ExecutorVersionInfo, DatasetLoaderVersionInfo]:
    """
    Set object version tags.

    Parameters
    ----------
    aggr_id: int
        Id of the object.
    version: int
        Version of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    key: str
        Key tag.
    values: list[str]
        Value tag.

    Returns
    -------
    Union[ ModelVersionInfo , ExecutorVersionInfo , DatasetLoaderVersionInfo]
        Instance with meta information.
    """
    model_type = ModelType(model_type)

    op = Operation(schema.Mutation)
    choice = schema.ObjectIdVersionInput(aggr_id=aggr_id, version=version)
    set_tag = op.set_object_version_tags(
        object_version=choice, key=key, values=values, model_type=model_type.name
    ).__as__(_object_version_map[model_type])
    set_tag.name()
    set_tag.version()
    set_tag.tags()
    model = send_graphql_request(op=op, json_response=False).set_object_version_tags
    return model


def reset_object_version_tags(
    aggr_id: int,
    version: int,
    model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType],
    key: str,
    values: list[str],
    new_key: Optional[str] = None,
) -> Union[ModelVersionInfo, ExecutorVersionInfo, DatasetLoaderVersionInfo]:
    """
    Reset object version tags.

    Parameters
    ----------
    aggr_id: int
        Id of the object.
    version: int
        Version of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    key: str
        Key tag.
    values: list[str]
        Value tag.
    new_key: Optional[str] = None
        New key of a tag.

    Returns
    -------
    Union[ ModelVersionInfo , ExecutorVersionInfo , DatasetLoaderVersionInfo]
        Instance with meta information.
    """
    model_type = ModelType(model_type)

    op = Operation(schema.Mutation)
    choice = schema.ObjectIdVersionInput(aggr_id=aggr_id, version=version)
    set_tag = op.reset_object_version_tags(
        object_version=choice, key=key, values=values, new_key=new_key, model_type=model_type.name
    ).__as__(_object_version_map[model_type])
    set_tag.name()
    set_tag.version()
    set_tag.tags()
    model = send_graphql_request(op=op, json_response=False).reset_object_version_tags
    return model


def delete_object_version_tag(
    aggr_id: int,
    version: int,
    model_type: Union[Literal["model", "executor", "dataset_loader"], ModelType],
    key: str,
    value: Optional[str] = None,
) -> Union[ModelVersionInfo, ExecutorVersionInfo, DatasetLoaderVersionInfo]:
    """
    Delete object version tag.

    Parameters
    ----------
    aggr_id: int
        Id of the object.
    version: int
        Version of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    key: str
        Key tag.
    value: Optional[str]=None
        value tag.

    Returns
    -------
    ModelVersion
        Instance with meta information.
    """
    model_type = ModelType(model_type)

    op = Operation(schema.Mutation)
    choice = schema.ObjectIdVersionInput(aggr_id=aggr_id, version=version)
    delete_tag = op.delete_object_version_tag(
        object_version=choice, key=key, value=value, model_type=model_type.name
    ).__as__(_object_version_map[model_type])
    delete_tag.name()
    delete_tag.version()
    delete_tag.tags()
    model = send_graphql_request(op=op, json_response=False).delete_object_version_tag
    return model


def delete_object(aggr_id: int, model_type: ModelType) -> bool:
    """
    Delete object and all of it's versions.

    Parameters
    ----------
    aggr_id: int
        Name of the object to delete.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    Returns
    -------
    bool
        Operation success status.
    """
    model_type = ModelType(model_type)

    op = Operation(schema.Mutation)
    op.delete_object(aggr_id=aggr_id, model_type=model_type.name)
    return send_graphql_request(op)["deleteObject"]


def delete_object_version(aggr_id: int, version: int, model_type: ModelType):
    """
    Delete version of a object.

    Parameters
    ----------
    aggr_id: int
        The name of the object.
    version: int
        The version of the object.
    model_type: Union[Literal['model', 'executor', 'dataset_loader'] , ModelType]
        Type of the entity. Possible values: ModelType.MODEL | ModelType.EXECUTOR | ModelType.DATASET_LOADER
    Returns
    -------
    None
    """
    model_type = ModelType(model_type)

    op = Operation(schema.Mutation)
    choice = schema.ObjectIdVersionInput(aggr_id=aggr_id, version=version)
    op.delete_object_version(object_version=choice, model_type=model_type.name).__as__(_object_map[model_type]).name()
    send_graphql_request(op, json_response=False)
