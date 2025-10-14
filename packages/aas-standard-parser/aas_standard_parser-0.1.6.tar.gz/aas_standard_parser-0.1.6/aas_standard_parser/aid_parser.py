"""This module provides functions to parse AID Submodels and extract MQTT interface descriptions."""
import base64
from typing import Dict, List

from basyx.aas.model import (
    Property,
    SubmodelElement,
    SubmodelElementCollection, SubmodelElementList, Submodel,
)

from aas_standard_parser.collection_helpers import find_by_semantic_id, find_all_by_semantic_id, find_by_id_short


class PropertyDetails:

    def __init__(self, href: str, keys: List[str]):
        self.href = href
        self.keys = keys


class IAuthenticationDetails:

    def __init__(self):
        # TODO: different implementations for different AID versions
        pass


class BasicAuthenticationDetails(IAuthenticationDetails):

    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password
        super().__init__()


class NoAuthenticationDetails(IAuthenticationDetails):

    def __init__(self):
        super().__init__()


class AIDParser():

    def __init__(self):
        pass

    def get_base_url_from_interface(self, aid_interface: SubmodelElementCollection) -> str:
        """Get the base address (EndpointMetadata.base) from a SMC describing an interface in the AID."""

        endpoint_metadata: SubmodelElementCollection | None = find_by_semantic_id(
            aid_interface.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/EndpointMetadata"
        )
        if endpoint_metadata is None:
            raise ValueError(f"'EndpointMetadata' SMC not found in the provided '{aid_interface.id_short}' SMC.")

        base: Property | None = find_by_semantic_id(
            endpoint_metadata.value, "https://www.w3.org/2019/wot/td#baseURI"
        )
        if base is None:
            raise ValueError("'base' Property not found in 'EndpointMetadata' SMC.")

        return base.value


    def create_property_to_href_map(self, aid_interface: SubmodelElementCollection) -> Dict[str, PropertyDetails]:
        """Find all first-level and nested properties in a provided SMC describing one interface in the AID.
        Map each property (either top-level or nested) to the according 'href' attribute.
        Nested properties are further mapped to the hierarchical list of keys
        that are necessary to extract their value from the payload of the interface.

        :param aid_interface: An SMC describing an interface in the AID.
        :return: A dictionary mapping each property (represented by its idShort-path) to PropertyDetails.
        """
        mapping: Dict[str, PropertyDetails] = {}

        interaction_metadata: SubmodelElementCollection | None = find_by_semantic_id(
            aid_interface.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/InteractionMetadata"
        )
        if interaction_metadata is None:
            raise ValueError(f"'InteractionMetadata' SMC not found in the provided '{aid_interface.id_short}' SMC.")

        properties: SubmodelElementCollection | None = find_by_semantic_id(
            interaction_metadata.value, "https://www.w3.org/2019/wot/td#PropertyAffordance"
        )
        if properties is None:
            raise ValueError("'properties' SMC not found in 'InteractionMetadata' SMC.")

        fl_properties: List[SubmodelElement] = find_all_by_semantic_id(
            properties.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/PropertyDefinition"
        )
        # TODO: some AIDs have typos in that semanticId but we only support the official ones
        #fl_properties_alternative: List[SubmodelElement] = find_all_by_semantic_id(
        #    properties.value, "https://admin-shell.io/idta/AssetInterfaceDescription/1/0/PropertyDefinition"
        #)
        #fl_properties.extend(fl_properties_alternative)
        if fl_properties is None:
            #raise ValueError(f"No first-level 'property' SMC not found in 'properties' SMC.")
            return {}

        def traverse_property(smc: SubmodelElementCollection, parent_path: str, href: str, key_path: List[str | int],
                              is_items=False, idx=None, is_top_level=False):
            # determine local key only if not top-level
            if not is_top_level:
                if is_items and idx is not None:
                    local_key = idx  # integer index
                else:
                    key_prop = find_by_semantic_id(
                        smc.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/key"
                    )
                    local_key = key_prop.value if key_prop else smc.id_short  # string
                new_key_path = key_path + [local_key]
            else:
                new_key_path = key_path  # top-level: no key added

            # register this property
            full_path = f"{parent_path}.{smc.id_short}"
            mapping[full_path] = PropertyDetails(href, new_key_path)

            # traverse nested "properties" or "items"
            # (nested properties = object members, nested items = array elements)
            # TODO: some apparently use the wrong semanticId:
            # "https://www.w3.org/2019/wot/td#PropertyAffordance"
            for nested_sem_id in [
                "https://www.w3.org/2019/wot/json-schema#properties",
                "https://www.w3.org/2019/wot/json-schema#items",
            ]:
                nested_group: SubmodelElementCollection | None = find_by_semantic_id(smc.value, nested_sem_id)
                if nested_group:
                    # attach the name of that SMC ("items" or "properties" or similar) to the key_path
                    full_path += "." + nested_group.id_short

                    # find all nested properties/items by semantic-ID
                    nested_properties: List[SubmodelElement] = find_all_by_semantic_id(
                        nested_group.value, "https://www.w3.org/2019/wot/json-schema#propertyName"
                    )
                    # TODO: some AIDs have typos or use wrong semanticIds but we only support the official ones
                    #nested_properties_alternative1: List[SubmodelElement] = find_all_by_semantic_id(
                    #    nested_group.value, "https://admin-shell.io/idta/AssetInterfaceDescription/1/0/PropertyDefinition"
                    #)
                    # nested_properties_alternative2: List[SubmodelElement] = find_all_by_semantic_id(
                    #    nested_group.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/PropertyDefinition"
                    # )
                    #nested_properties.extend(nested_properties_alternative1)
                    #nested_properties.extend(nested_properties_alternative2)

                    # traverse all nested properties/items recursively
                    for idx, nested in enumerate(nested_properties):
                        if nested_sem_id.endswith("#items"):
                            # for arrays: append index instead of property key
                            traverse_property(nested, full_path, href, new_key_path, is_items=True, idx=idx)
                        else:
                            traverse_property(nested, full_path, href, new_key_path)

        # process all first-level properties
        for fl_property in fl_properties:
            forms: SubmodelElementCollection | None = find_by_semantic_id(
                fl_property.value, "https://www.w3.org/2019/wot/td#hasForm"
            )
            if forms is None:
                raise ValueError(f"'forms' SMC not found in '{fl_property.id_short}' SMC.")

            href: Property | None = find_by_semantic_id(
                forms.value, "https://www.w3.org/2019/wot/hypermedia#hasTarget"
            )
            if href is None:
                raise ValueError("'href' Property not found in 'forms' SMC.")

            href_value = href.value
            idshort_path_prefix = f"{aid_interface.id_short}.{interaction_metadata.id_short}.{properties.id_short}"

            traverse_property(
                fl_property,
                idshort_path_prefix,
                href_value,
                [],
                is_top_level=True
            )

        return mapping


    def parse_security(self, aid_interface: SubmodelElementCollection) -> IAuthenticationDetails:
        """Extract the authentication details (EndpointMetadata.security) from the provided interface in the AID.

        :param aid_interface: An SMC describing an interface in the AID.
        :return: A subtype of IAuthenticationDetails with details depending on the specified authentication method for the interface.
        """
        endpoint_metadata: SubmodelElementCollection | None = find_by_semantic_id(
            aid_interface.value, "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/EndpointMetadata"
        )
        if endpoint_metadata is None:
            raise ValueError(f"'EndpointMetadata' SMC not found in the provided '{aid_interface.id_short}' SMC.")

        security: SubmodelElementList | None = find_by_semantic_id(
            endpoint_metadata.value, "https://www.w3.org/2019/wot/td#hasSecurityConfiguration"
        )
        if security is None:
            raise ValueError("'security' SML not found in 'EndpointMetadata' SMC.")

        # TODO: resolve the full reference(s)
        # for now, assume there is only one reference to the security in use
        # -> access SML[0]
        # assume that this ReferenceElement points to a security scheme in this very AID SM
        # -> can just use the last key to determine the type of security
        sc_idshort = security.value[0].value.key[-1].value

        # get the securityDefinitions SMC
        security_definitions: SubmodelElementCollection | None = find_by_semantic_id(
            endpoint_metadata.value, "https://www.w3.org/2019/wot/td#definesSecurityScheme"
        )
        if security_definitions is None:
            raise ValueError("'securityDefinitions' SMC not found in 'EndpointMetadata' SMC.")

        # find the security scheme SMC with the same idShort as mentioned in the reference "sc"
        referenced_security: SubmodelElementCollection | None = find_by_id_short(
            security_definitions.value, sc_idshort
        )
        if referenced_security is None:
            raise ValueError(f"Referenced security scheme '{sc_idshort}' SMC not found in 'securityDefinitions' SMC")

        # get the name of the security scheme
        scheme: Property | None = find_by_semantic_id(
            referenced_security.value, "https://www.w3.org/2019/wot/security#SecurityScheme"
        )
        if scheme is None:
            raise ValueError(f"'scheme' Property not found in referenced security scheme '{sc_idshort}' SMC.")

        auth_details: IAuthenticationDetails = None

        match scheme.value:
            case "nosec":
                auth_details = NoAuthenticationDetails()

            case "basic":
                basic_sc_name: Property | None = find_by_semantic_id(
                    referenced_security.value, "https://www.w3.org/2019/wot/security#name"
                )
                if basic_sc_name is None:
                    raise ValueError("'name' Property not found in 'basic_sc' SMC")

                auth_base64 = basic_sc_name.value
                auth_plain = base64.b64decode(auth_base64).decode("utf-8")
                auth_details = BasicAuthenticationDetails(auth_plain.split(":")[0], auth_plain.split(":")[1])

            # TODO: remaining cases
            case "digest":
                pass
            case "bearer":
                pass
            case "psk":
                pass
            case "oauth2":
                pass
            case "apikey":
                pass
            case "auto":
                pass

        return auth_details
