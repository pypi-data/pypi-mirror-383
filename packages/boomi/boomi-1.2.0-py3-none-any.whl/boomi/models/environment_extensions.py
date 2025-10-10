
from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL
from .pgp_certificates import PgpCertificates
from .connections import Connections
from .cross_references import CrossReferences
from .operations import Operations
from .override_process_properties import OverrideProcessProperties
from .properties import Properties
from .shared_communications import SharedCommunications
from .trading_partners import TradingPartners


@JsonMap(
    {
        "pgp_certificates": "PGPCertificates",
        "cross_references": "crossReferences",
        "environment_id": "environmentId",
        "extension_group_id": "extensionGroupId",
        "id_": "id",
        "process_properties": "processProperties",
        "shared_communications": "sharedCommunications",
        "trading_partners": "tradingPartners",
    }
)
class EnvironmentExtensions(BaseModel):
    """EnvironmentExtensions

    :param pgp_certificates: pgp_certificates, defaults to None
    :type pgp_certificates: PgpCertificates, optional
    :param connections: connections, defaults to None
    :type connections: Connections, optional
    :param cross_references: cross_references, defaults to None
    :type cross_references: CrossReferences, optional
    :param environment_id: The ID of the environment., defaults to None
    :type environment_id: str, optional
    :param extension_group_id: The synthesized ID of the process belonging to a multi-install integration pack to which the extension values apply, if applicable. For more information, see the section in the Working with Environment Extensions subtopic about multi-install integration packs., defaults to None
    :type extension_group_id: str, optional
    :param id_: The ID of the object. This can be either of the following:\<br /\> 1. The value of environmentId.\<br /\> 2. A conceptual ID synthesized from the environment ID \(environmentId\) and the ID of the multi-install integration pack to which the extension values apply \(extensionGroupId\)., defaults to None
    :type id_: str, optional
    :param operations: operations, defaults to None
    :type operations: Operations, optional
    :param partial: Supplied only in an UPDATE operation. \<br /\>-   If set to true, indicates that the request includes only a subset of environment extension values to update. \<br /\> -   If set to false, indicates that the request includes the full set of environment extension values to update. Values not included in the request are reset to use their default values., defaults to None
    :type partial: bool, optional
    :param process_properties: process_properties, defaults to None
    :type process_properties: OverrideProcessProperties, optional
    :param properties: properties, defaults to None
    :type properties: Properties, optional
    :param shared_communications: shared_communications, defaults to None
    :type shared_communications: SharedCommunications, optional
    :param trading_partners: trading_partners, defaults to None
    :type trading_partners: TradingPartners, optional
    """

    def __init__(
        self,
        pgp_certificates: PgpCertificates = SENTINEL,
        connections: Connections = SENTINEL,
        cross_references: CrossReferences = SENTINEL,
        operations: Operations = SENTINEL,
        process_properties: OverrideProcessProperties = SENTINEL,
        properties: Properties = SENTINEL,
        shared_communications: SharedCommunications = SENTINEL,
        trading_partners: TradingPartners = SENTINEL,
        environment_id: str = SENTINEL,
        extension_group_id: str = SENTINEL,
        id_: str = SENTINEL,
        partial: bool = SENTINEL,
        **kwargs,
    ):
        """EnvironmentExtensions

        :param pgp_certificates: pgp_certificates, defaults to None
        :type pgp_certificates: PgpCertificates, optional
        :param connections: connections, defaults to None
        :type connections: Connections, optional
        :param cross_references: cross_references, defaults to None
        :type cross_references: CrossReferences, optional
        :param environment_id: The ID of the environment., defaults to None
        :type environment_id: str, optional
        :param extension_group_id: The synthesized ID of the process belonging to a multi-install integration pack to which the extension values apply, if applicable. For more information, see the section in the Working with Environment Extensions subtopic about multi-install integration packs., defaults to None
        :type extension_group_id: str, optional
        :param id_: The ID of the object. This can be either of the following:\<br /\> 1. The value of environmentId.\<br /\> 2. A conceptual ID synthesized from the environment ID \(environmentId\) and the ID of the multi-install integration pack to which the extension values apply \(extensionGroupId\)., defaults to None
        :type id_: str, optional
        :param operations: operations, defaults to None
        :type operations: Operations, optional
        :param partial: Supplied only in an UPDATE operation. \<br /\>-   If set to true, indicates that the request includes only a subset of environment extension values to update. \<br /\> -   If set to false, indicates that the request includes the full set of environment extension values to update. Values not included in the request are reset to use their default values., defaults to None
        :type partial: bool, optional
        :param process_properties: process_properties, defaults to None
        :type process_properties: OverrideProcessProperties, optional
        :param properties: properties, defaults to None
        :type properties: Properties, optional
        :param shared_communications: shared_communications, defaults to None
        :type shared_communications: SharedCommunications, optional
        :param trading_partners: trading_partners, defaults to None
        :type trading_partners: TradingPartners, optional
        """
        if pgp_certificates is not SENTINEL:
            self.pgp_certificates = self._define_object(pgp_certificates, PgpCertificates)
        if connections is not SENTINEL:
            self.connections = self._define_object(connections, Connections)
        if cross_references is not SENTINEL:
            self.cross_references = self._define_object(cross_references, CrossReferences)
        if environment_id is not SENTINEL:
            self.environment_id = environment_id
        if extension_group_id is not SENTINEL:
            self.extension_group_id = extension_group_id
        if id_ is not SENTINEL:
            self.id_ = id_
        if operations is not SENTINEL:
            self.operations = self._define_object(operations, Operations)
        if partial is not SENTINEL:
            self.partial = partial
        if process_properties is not SENTINEL:
            self.process_properties = self._define_object(
                process_properties, OverrideProcessProperties
            )
        if properties is not SENTINEL:
            self.properties = self._define_object(properties, Properties)
        if shared_communications is not SENTINEL:
            self.shared_communications = self._define_object(
                shared_communications, SharedCommunications
            )
        if trading_partners is not SENTINEL:
            self.trading_partners = self._define_object(trading_partners, TradingPartners)
        self._kwargs = kwargs
