# Fhircraft modules
from enum import Enum

# Standard modules
from typing import Literal, Optional, Union

# Pydantic modules
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.fields import FieldInfo

import fhircraft
import fhircraft.fhir.resources.validators as fhir_validators
from fhircraft.fhir.resources.base import FHIRBaseModel
from fhircraft.fhir.resources.datatypes.primitives import *

NoneType = type(None)

# Dynamic modules

from typing import List, Literal, Optional

from fhircraft.fhir.resources.base import FHIRBaseModel
from fhircraft.fhir.resources.datatypes.primitives import (
    Boolean,
    Canonical,
    Code,
    DateTime,
    Id,
    Markdown,
    String,
    Uri,
)
from fhircraft.fhir.resources.datatypes.R4B.complex_types import (
    BackboneElement,
    CodeableConcept,
    Coding,
    ContactDetail,
    Element,
    Extension,
    Identifier,
    Meta,
    Narrative,
    Resource,
    UsageContext,
)

from .element_definition import ElementDefinition


class StructureDefinitionMapping(BackboneElement):
    identity: Id = Field(
        description="Internal id when this mapping is used",
    )
    identity_ext: Optional[Element] = Field(
        description="Placeholder element for identity extensions",
        default=None,
        alias="_identity",
    )
    uri: Optional[Uri] = Field(
        description="Identifies what this mapping refers to",
        default=None,
    )
    uri_ext: Optional[Element] = Field(
        description="Placeholder element for uri extensions",
        default=None,
        alias="_uri",
    )
    name: Optional[String] = Field(
        description="Names what this mapping refers to",
        default=None,
    )
    name_ext: Optional[Element] = Field(
        description="Placeholder element for name extensions",
        default=None,
        alias="_name",
    )
    comment: Optional[String] = Field(
        description="Versions, Issues, Scope limitations etc.",
        default=None,
    )
    comment_ext: Optional[Element] = Field(
        description="Placeholder element for comment extensions",
        default=None,
        alias="_comment",
    )

    # @field_validator(
    #     *(
    #         "comment",
    #         "name",
    #         "uri",
    #         "identity",
    #         "modifierExtension",
    #         "extension",
    #         "modifierExtension",
    #         "extension",
    #         "modifierExtension",
    #         "extension",
    #         "modifierExtension",
    #         "extension",
    #     ),
    #     mode="after",
    #     check_fields=None,
    # )
    # @classmethod
    # def FHIR_ele_1_constraint_validator(cls, value):
    #     return fhir_validators.validate_element_constraint(
    #         cls,
    #         value,
    #         expression="hasValue() or (children().count() > id.count())",
    #         human="All FHIR elements must have a @value or children",
    #         key="ele-1",
    #         severity="error",
    #     )


class StructureDefinitionContext(BackboneElement):
    type: Code = Field(
        description="fhirpath | element | extension",
    )
    type_ext: Optional[Element] = Field(
        description="Placeholder element for type extensions",
        default=None,
        alias="_type",
    )
    expression: String = Field(
        description="Where the extension can be used in instances",
    )
    expression_ext: Optional[Element] = Field(
        description="Placeholder element for expression extensions",
        default=None,
        alias="_expression",
    )


#     @field_validator(
#         *(
#             "expression",
#             "type",
#             "modifierExtension",
#             "extension",
#             "modifierExtension",
#             "extension",
#         ),
#         mode="after",
#         check_fields=None,
#     )
#     @classmethod
#     def FHIR_ele_1_constraint_validator(cls, value):
#         return fhir_validators.validate_element_constraint(
#             cls,
#             value,
#             expression="hasValue() or (children().count() > id.count())",
#             human="All FHIR elements must have a @value or children",
#             key="ele-1",
#             severity="error",
#         )


class StructureDefinitionSnapshot(BackboneElement):
    element: List[ElementDefinition] = Field(
        description="Definition of elements in the resource (if no StructureDefinition)",
    )


#     @field_validator(
#         *("element", "modifierExtension", "extension"), mode="after", check_fields=None
#     )
#     @classmethod
#     def FHIR_ele_1_constraint_validator(cls, value):
#         return fhir_validators.validate_element_constraint(
#             cls,
#             value,
#             expression="hasValue() or (children().count() > id.count())",
#             human="All FHIR elements must have a @value or children",
#             key="ele-1",
#             severity="error",
#         )

#     @field_validator(*("element",), mode="after", check_fields=None)
#     @classmethod
#     def FHIR_sdf_10_constraint_validator(cls, value):
#         return fhir_validators.validate_element_constraint(
#             cls,
#             value,
#             expression="binding.empty() or binding.valueSet.exists() or binding.description.exists()",
#             human="provide either a binding reference or a description (or both)",
#             key="sdf-10",
#             severity="error",
#         )


class StructureDefinitionDifferential(BackboneElement):
    element: List[ElementDefinition] = Field(
        description="Definition of elements in the resource (if no StructureDefinition)",
    )

    @field_validator(
        *("element", "modifierExtension", "extension"), mode="after", check_fields=None
    )
    @classmethod
    def FHIR_ele_1_constraint_validator(cls, value):
        return fhir_validators.validate_element_constraint(
            cls,
            value,
            expression="hasValue() or (children().count() > id.count())",
            human="All FHIR elements must have a @value or children",
            key="ele-1",
            severity="error",
        )


class StructureDefinition(FHIRBaseModel):
    id: Optional[String] = Field(
        description="Logical id of this artifact",
        default=None,
    )
    id_ext: Optional[Element] = Field(
        description="Placeholder element for id extensions",
        default=None,
        alias="_id",
    )
    # meta: Optional[Meta] = Field(
    #     description=None,
    # )
    implicitRules: Optional[Uri] = Field(
        description="A set of rules under which this content was created",
        default=None,
    )
    implicitRules_ext: Optional[Element] = Field(
        description="Placeholder element for implicitRules extensions",
        default=None,
        alias="_implicitRules",
    )
    language: Optional[Code] = Field(
        description="Language of the resource content",
        default=None,
    )
    language_ext: Optional[Element] = Field(
        description="Placeholder element for language extensions",
        default=None,
        alias="_language",
    )
    text: Optional[Narrative] = Field(
        description="Text summary of the resource, for human interpretation",
        default=None,
    )
    contained: Optional[List[Resource]] = Field(
        description="Contained, inline Resources",
        default=None,
    )
    extension: Optional[List[Extension]] = Field(
        description="Additional content defined by implementations",
        default=None,
    )
    modifierExtension: Optional[List[Extension]] = Field(
        description="Extensions that cannot be ignored",
        default=None,
    )
    url: Uri = Field(
        description="Canonical identifier for this structure definition, represented as a URI (globally unique)",
    )
    url_ext: Optional[Element] = Field(
        description="Placeholder element for url extensions",
        default=None,
        alias="_url",
    )
    identifier: Optional[List[Identifier]] = Field(
        description="Additional identifier for the structure definition",
        default=None,
    )
    version: Optional[String] = Field(
        description="Business version of the structure definition",
        default=None,
    )
    version_ext: Optional[Element] = Field(
        description="Placeholder element for version extensions",
        default=None,
        alias="_version",
    )
    name: String = Field(
        description="Name for this structure definition (computer friendly)",
    )
    name_ext: Optional[Element] = Field(
        description="Placeholder element for name extensions",
        default=None,
        alias="_name",
    )
    title: Optional[String] = Field(
        description="Name for this structure definition (human friendly)",
        default=None,
    )
    title_ext: Optional[Element] = Field(
        description="Placeholder element for title extensions",
        default=None,
        alias="_title",
    )
    status: Code = Field(
        description="draft | active | retired | unknown",
    )
    status_ext: Optional[Element] = Field(
        description="Placeholder element for status extensions",
        default=None,
        alias="_status",
    )
    experimental: Optional[Boolean] = Field(
        description="For testing purposes, not real usage",
        default=None,
    )
    experimental_ext: Optional[Element] = Field(
        description="Placeholder element for experimental extensions",
        default=None,
        alias="_experimental",
    )
    date: Optional[DateTime] = Field(
        description="Date last changed",
        default=None,
    )
    date_ext: Optional[Element] = Field(
        description="Placeholder element for date extensions",
        default=None,
        alias="_date",
    )
    publisher: Optional[String] = Field(
        description="Name of the publisher (organization or individual)",
        default=None,
    )
    publisher_ext: Optional[Element] = Field(
        description="Placeholder element for publisher extensions",
        default=None,
        alias="_publisher",
    )
    contact: Optional[List[ContactDetail]] = Field(
        description="Contact details for the publisher",
        default=None,
    )
    description: Optional[Markdown] = Field(
        description="Natural language description of the structure definition",
        default=None,
    )
    description_ext: Optional[Element] = Field(
        description="Placeholder element for description extensions",
        default=None,
        alias="_description",
    )
    useContext: Optional[List[UsageContext]] = Field(
        description="The context that the content is intended to support",
        default=None,
    )
    jurisdiction: Optional[List[CodeableConcept]] = Field(
        description="Intended jurisdiction for structure definition (if applicable)",
        default=None,
    )
    purpose: Optional[Markdown] = Field(
        description="Why this structure definition is defined",
        default=None,
    )
    purpose_ext: Optional[Element] = Field(
        description="Placeholder element for purpose extensions",
        default=None,
        alias="_purpose",
    )
    copyright: Optional[Markdown] = Field(
        description="Use and/or publishing restrictions",
        default=None,
    )
    copyright_ext: Optional[Element] = Field(
        description="Placeholder element for copyright extensions",
        default=None,
        alias="_copyright",
    )
    keyword: Optional[List[Coding]] = Field(
        description="Assist with indexing and finding",
        default=None,
    )
    fhirVersion: Optional[Code] = Field(
        description="FHIR Version this StructureDefinition targets",
        default=None,
    )
    fhirVersion_ext: Optional[Element] = Field(
        description="Placeholder element for fhirVersion extensions",
        default=None,
        alias="_fhirVersion",
    )
    mapping: Optional[List[StructureDefinitionMapping]] = Field(
        description="External specification that the content is mapped to",
        default=None,
    )
    kind: Code = Field(
        description="primitive-type | complex-type | resource | logical",
    )
    kind_ext: Optional[Element] = Field(
        description="Placeholder element for kind extensions",
        default=None,
        alias="_kind",
    )
    abstract: Boolean = Field(
        description="Whether the structure is abstract",
    )
    abstract_ext: Optional[Element] = Field(
        description="Placeholder element for abstract extensions",
        default=None,
        alias="_abstract",
    )
    context: Optional[List[StructureDefinitionContext]] = Field(
        description="If an extension, where it can be used in instances",
        default=None,
    )
    contextInvariant: Optional[List[String]] = Field(
        description="FHIRPath invariants - when the extension can be used",
        default=None,
    )
    contextInvariant_ext: Optional[Element] = Field(
        description="Placeholder element for contextInvariant extensions",
        default=None,
        alias="_contextInvariant",
    )
    type: Uri = Field(
        description="Type defined or constrained by this structure",
    )
    type_ext: Optional[Element] = Field(
        description="Placeholder element for type extensions",
        default=None,
        alias="_type",
    )
    baseDefinition: Optional[Canonical] = Field(
        description="Definition that this type is constrained/specialized from",
        default=None,
    )
    baseDefinition_ext: Optional[Element] = Field(
        description="Placeholder element for baseDefinition extensions",
        default=None,
        alias="_baseDefinition",
    )
    derivation: Optional[Code] = Field(
        description="specialization | constraint - How relates to base definition",
        default=None,
    )
    derivation_ext: Optional[Element] = Field(
        description="Placeholder element for derivation extensions",
        default=None,
        alias="_derivation",
    )
    snapshot: Optional["StructureDefinitionSnapshot"] = Field(
        description="Snapshot view of the structure",
        default=None,
    )
    differential: Optional[StructureDefinitionDifferential] = Field(
        description="Differential view of the structure",
        default=None,
    )
    resourceType: Literal["StructureDefinition"] = Field(
        description=None,
    )

    # @field_validator(
    #     *(
    #         "differential",
    #         "snapshot",
    #         "derivation",
    #         "baseDefinition",
    #         "type",
    #         "contextInvariant",
    #         "context",
    #         "abstract",
    #         "kind",
    #         "mapping",
    #         "fhirVersion",
    #         "keyword",
    #         "copyright",
    #         "purpose",
    #         "jurisdiction",
    #         "useContext",
    #         "description",
    #         "contact",
    #         "publisher",
    #         "date",
    #         "experimental",
    #         "status",
    #         "title",
    #         "name",
    #         "version",
    #         "identifier",
    #         "url",
    #         "modifierExtension",
    #         "extension",
    #         "text",
    #         "language",
    #         "implicitRules",
    #         "meta",
    #     ),
    #     mode="after",
    #     check_fields=None,
    # )
    # @classmethod
    # def FHIR_ele_1_constraint_validator(cls, value):
    #     return fhir_validators.validate_element_constraint(
    #         cls,
    #         value,
    #         expression="hasValue() or (children().count() > id.count())",
    #         human="All FHIR elements must have a @value or children",
    #         key="ele-1",
    #         severity="error",
    #     )

    # @field_validator(
    #     *("modifierExtension", "extension"), mode="after", check_fields=None
    # )
    # @classmethod
    # def FHIR_ext_1_constraint_validator(cls, value):
    #     return fhir_validators.validate_element_constraint(
    #         cls,
    #         value,
    #         expression="extension.exists() != value.exists()",
    #         human="Must have either extensions or value[x], not both",
    #         key="ext-1",
    #         severity="error",
    #     )

    # @field_validator(*("mapping",), mode="after", check_fields=None)
    # @classmethod
    # def FHIR_sdf_2_constraint_validator(cls, value):
    #     return fhir_validators.validate_element_constraint(
    #         cls,
    #         value,
    #         expression="name.exists() or uri.exists()",
    #         human="Must have at least a name or a uri (or both)",
    #         key="sdf-2",
    #         severity="error",
    #     )

    # @field_validator(*("snapshot",), mode="after", check_fields=None)
    # @classmethod
    # def FHIR_sdf_3_constraint_validator(cls, value):
    #     return fhir_validators.validate_element_constraint(
    #         cls,
    #         value,
    #         expression="element.all(definition.exists() and min.exists() and max.exists())",
    #         human="Each element definition in a snapshot must have a formal definition and cardinalities",
    #         key="sdf-3",
    #         severity="error",
    #     )

    # @field_validator(*("snapshot",), mode="after", check_fields=None)
    # @classmethod
    # def FHIR_sdf_8_constraint_validator(cls, value):
    #     return fhir_validators.validate_element_constraint(
    #         cls,
    #         value,
    #         expression="(%resource.kind = 'logical' or element.first().path = %resource.type) and element.tail().all(path.startsWith(%resource.snapshot.element.first().path&'.'))",
    #         human="All snapshot elements must start with the StructureDefinition's specified type for non-logical models, or with the same type name for logical models",
    #         key="sdf-8",
    #         severity="error",
    #     )

    # @field_validator(*("snapshot",), mode="after", check_fields=None)
    # @classmethod
    # def FHIR_sdf_8b_constraint_validator(cls, value):
    #     return fhir_validators.validate_element_constraint(
    #         cls,
    #         value,
    #         expression="element.all(base.exists())",
    #         human="All snapshot elements must have a base definition",
    #         key="sdf-8b",
    #         severity="error",
    #     )

    # @field_validator(*("differential",), mode="after", check_fields=None)
    # @classmethod
    # def FHIR_sdf_20_constraint_validator(cls, value):
    #     return fhir_validators.validate_element_constraint(
    #         cls,
    #         value,
    #         expression="element.where(path.contains('.').not()).slicing.empty()",
    #         human="No slicing on the root element",
    #         key="sdf-20",
    #         severity="error",
    #     )

    # @field_validator(*("differential",), mode="after", check_fields=None)
    # @classmethod
    # def FHIR_sdf_8a_constraint_validator(cls, value):
    #     return fhir_validators.validate_element_constraint(
    #         cls,
    #         value,
    #         expression="(%resource.kind = 'logical' or element.first().path.startsWith(%resource.type)) and (element.tail().empty() or element.tail().all(path.startsWith(%resource.differential.element.first().path.replaceMatches('\\..*','')&'.')))",
    #         human="In any differential, all the elements must start with the StructureDefinition's specified type for non-logical models, or with the same type name for logical models",
    #         key="sdf-8a",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_dom_2_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="contained.contained.empty()",
    #         human="If the resource is contained in another resource, it SHALL NOT contain nested Resources",
    #         key="dom-2",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_dom_3_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="contained.where((('#'+id in (%resource.descendants().reference | %resource.descendants().as(canonical) | %resource.descendants().as(uri) | %resource.descendants().as(url))) or descendants().where(reference = '#').exists() or descendants().where(as(canonical) = '#').exists() or descendants().where(as(canonical) = '#').exists()).not()).trace('unmatched', id).empty()",
    #         human="If the resource is contained in another resource, it SHALL be referred to from elsewhere in the resource or SHALL refer to the containing resource",
    #         key="dom-3",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_dom_4_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="contained.meta.versionId.empty() and contained.meta.lastUpdated.empty()",
    #         human="If a resource is contained in another resource, it SHALL NOT have a meta.versionId or a meta.lastUpdated",
    #         key="dom-4",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_dom_5_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="contained.meta.security.empty()",
    #         human="If a resource is contained in another resource, it SHALL NOT have a security label",
    #         key="dom-5",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_dom_6_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="text.`div`.exists()",
    #         human="A resource should have narrative for robust management",
    #         key="dom-6",
    #         severity="warning",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_0_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="name.matches('[A-Z]([A-Za-z0-9_]){0,254}')",
    #         human="Name should be usable as an identifier for the module by machine processing applications such as code generation",
    #         key="sdf-0",
    #         severity="warning",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_1_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="derivation = 'constraint' or snapshot.element.select(path).isDistinct()",
    #         human="Element paths must be unique unless the structure is a constraint",
    #         key="sdf-1",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_15a_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="(kind!='logical'  and differential.element.first().path.contains('.').not()) implies differential.element.first().type.empty()",
    #         human='If the first element in a differential has no "." in the path and it\'s not a logical model, it has no type',
    #         key="sdf-15a",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_4_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="abstract = true or baseDefinition.exists()",
    #         human="If the structure is not abstract, then there SHALL be a baseDefinition",
    #         key="sdf-4",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_5_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="type != 'Extension' or derivation = 'specialization' or (context.exists())",
    #         human="If the structure defines an extension then the structure must have context information",
    #         key="sdf-5",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_6_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="snapshot.exists() or differential.exists()",
    #         human="A structure must have either a differential, or a snapshot (or both)",
    #         key="sdf-6",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_9_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="children().element.where(path.contains('.').not()).label.empty() and children().element.where(path.contains('.').not()).code.empty() and children().element.where(path.contains('.').not()).requirements.empty()",
    #         human='In any snapshot or differential, no label, code or requirements on an element without a "." in the path (e.g. the first element)',
    #         key="sdf-9",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_11_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="kind != 'logical' implies snapshot.empty() or snapshot.element.first().path = type",
    #         human="If there's a type, its content must match the path name in the first element of a snapshot",
    #         key="sdf-11",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_14_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="snapshot.element.all(id.exists()) and differential.element.all(id.exists())",
    #         human="All element definitions must have an id",
    #         key="sdf-14",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_15_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="kind!='logical' implies snapshot.element.first().type.empty()",
    #         human="The first element in a snapshot has no type unless model is a logical model.",
    #         key="sdf-15",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_16_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="snapshot.element.all(id.exists()) and snapshot.element.id.trace('ids').isDistinct()",
    #         human="All element definitions must have unique ids (snapshot)",
    #         key="sdf-16",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_17_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="differential.element.all(id.exists()) and differential.element.id.trace('ids').isDistinct()",
    #         human="All element definitions must have unique ids (diff)",
    #         key="sdf-17",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_18_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="contextInvariant.exists() implies type = 'Extension'",
    #         human="Context Invariants can only be used for extensions",
    #         key="sdf-18",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_19_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="url.startsWith('http://hl7.org/fhir/StructureDefinition') implies (differential.element.type.code.all(matches('^[a-zA-Z0-9]+$') or matches('^http:\\/\\/hl7\\.org\\/fhirpath\\/System\\.[A-Z][A-Za-z]+$')) and snapshot.element.type.code.all(matches('^[a-zA-Z0-9\\.]+$') or matches('^http:\\/\\/hl7\\.org\\/fhirpath\\/System\\.[A-Z][A-Za-z]+$')))",
    #         human="FHIR Specification models only use FHIR defined types",
    #         key="sdf-19",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_21_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="differential.element.defaultValue.exists() implies (derivation = 'specialization')",
    #         human="Default values can only be specified on specializations",
    #         key="sdf-21",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_22_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="url.startsWith('http://hl7.org/fhir/StructureDefinition') implies (snapshot.element.defaultValue.empty() and differential.element.defaultValue.empty())",
    #         human="FHIR Specification models never have default values",
    #         key="sdf-22",
    #         severity="error",
    #     )

    # @model_validator(mode="after")
    # def FHIR_sdf_23_constraint_model_validator(self):
    #     return fhir_validators.validate_model_constraint(
    #         self,
    #         expression="(snapshot | differential).element.all(path.contains('.').not() implies sliceName.empty())",
    #         human="No slice name on root",
    #         key="sdf-23",
    #         severity="error",
    #     )


StructureDefinitionMapping.model_rebuild()

StructureDefinitionContext.model_rebuild()

StructureDefinitionSnapshot.model_rebuild()

StructureDefinitionDifferential.model_rebuild()

StructureDefinition.model_rebuild()
StructureDefinition.model_rebuild()
