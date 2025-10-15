"""
Helper tools to work with identifiers registry.

https://identifiers.org/
https://docs.identifiers.org/articles/api.html
"""

from __future__ import annotations

import inspect
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

import pymetadata
from pymetadata import log
from pymetadata.cache import DataclassJSONEncoder, read_json_cache, write_json_cache
from pymetadata.console import console

logger = log.get_logger(__name__)


@dataclass
class Resource:
    """Resource."""

    id: Optional[int]
    providerCode: str
    name: str
    urlPattern: str
    mirId: Optional[str] = field(repr=False)
    description: str = field(repr=False)
    official: bool = field(repr=False)

    sampleId: Optional[str] = field(repr=False)
    resourceHomeUrl: Optional[str] = field(repr=False)
    institution: dict = field(repr=False)
    location: dict = field(repr=False)
    deprecated: bool = field(repr=False)
    deprecationDate: str = field(repr=False)
    protectedUrls: bool = field(repr=False, default=False)
    renderProtectedLanding: bool = field(repr=False, default=False)
    authHelpUrl: Optional[str] = field(repr=False, default=None)
    authHelpDescription: Optional[str] = field(repr=False, default=None)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Resource:
        """Handle additional keyword arguments."""
        return cls(
            **{k: v for k, v in d.items() if k in inspect.signature(cls).parameters}
        )


@dataclass
class Namespace:
    """Namespace."""

    id: Optional[str]
    prefix: Optional[str]
    name: str
    pattern: str
    namespaceEmbeddedInLui: bool
    description: str = field(repr=False)
    mirId: Optional[str] = field(repr=False, default=None)
    resources: Optional[List] = field(repr=False, default=None)
    created: Optional[str] = field(repr=False, default=None)
    modified: Optional[str] = field(repr=False, default=None)
    sampleId: Optional[str] = field(repr=False, default=None)
    deprecated: bool = field(repr=False, default=False)
    deprecationDate: Optional[str] = field(repr=False, default=None)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Namespace:
        """Handle additional keyword arguments."""
        return cls(
            **{k: v for k, v in d.items() if k in inspect.signature(cls).parameters}
        )

    def __post_init__(self) -> None:
        """Set resources."""
        if self.resources is not None:
            self.resources = [Resource.from_dict(d) for d in self.resources]
        else:
            self.resources = list()


def ols_namespaces() -> Dict[str, Namespace]:
    """Define Ontologies available from OLS but not in identifiers.org."""
    ols_info: Dict = {
        "deprecated": False,
        "deprecationDate": None,
        "institution": {
            "description": "At EMBL-EBI, we make the "
            "world’s public biological data "
            "freely available to the "
            "scientific community via a "
            "range of services and tools, "
            "perform basic research and "
            "provide professional training "
            "in bioinformatics. \n"
            "We are part of the European "
            "Molecular Biology Laboratory "
            "(EMBL), an international, "
            "innovative and "
            "interdisciplinary research "
            "organisation funded by 26 "
            "member states and two "
            "associate member states.",
            "homeUrl": "https://www.ebi.ac.uk",
            "id": 2,
            "location": {"countryCode": "GB", "countryName": "United Kingdom"},
            "name": "European Bioinformatics Institute",
            "rorId": "https://ror.org/02catss52",
        },
        "location": {"countryCode": "GB", "countryName": "United Kingdom"},
        "official": False,
        "providerCode": "ols",
    }

    # Custom namespaces for OLS ontology, for simple support
    namespaces = [
        Namespace(
            id=None,
            prefix="omim",
            pattern=r"^MI:\d+$",
            name="OMIM",
            description="Molecular Interactions Controlled Vocabulary",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="dron",
            pattern=r"^DRON:\d+$",
            name="DRON",
            description="The drug ontology",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="cmo",
            pattern=r"^CMO:\d+$",
            name="Chemical methods ontology",
            description="Morphological and physiological measurement records "
            "generated from clinical and model organism research and health programs.",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="chmo",
            pattern=r"^CHMO:\d+$",
            name="Chemical methods ontology",
            description="CHMO, the chemical methods ontology",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="vto",
            pattern=r"^VTO:\d+$",
            name="Vertebrate Taxonomy Ontology",
            description="VTO Vertebrate Taxonomy Ontology",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="opmi",
            pattern=r"^OPMI:\d+$",
            name="Ontology of Precision Medicine and Investigation",
            description="OPMI: Ontology of Precision Medicine and Investigation",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="atol",
            pattern=r"^ATOL:\d+$",
            name="ATOL",
            description="Animal Trait Ontology for Livestock",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="nbo",
            pattern=r"^NBO:\d+$",
            name="NBO",
            description="Neuro Behavior Ontology",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="scdo",
            pattern=r"^SCDO:\d+$",
            name="Sickle Cell Disease Ontology",
            description="Sickle Cell Disease Ontology",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="fix",
            pattern=r"^FIX:\d+$",
            name="Physico-chemical methods and properties Ontology",
            description="Physico-chemical methods and properties Ontology",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="oba",
            pattern=r"^OBA:\d+$",
            name="Ontology of Biological Attributes",
            description="PubChem is an open chemistry database at the National "
            "Institutes of Health (NIH).",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="mmo",
            pattern=r"^MMO:\d+$",
            name="Measurement method ontology",
            description="Measurement method ontology",
            namespaceEmbeddedInLui=True,
        ),
        Namespace(
            id=None,
            prefix="symp",
            pattern=r"^SYMP:\d+$",
            name="Symptom ontology",
            description="The Symptom Ontology has been developed as a standardized ontology for symptoms of human diseases.",
            namespaceEmbeddedInLui=True,
        ),
    ]

    for ns in namespaces:
        if not ns.resources:
            ns.resources = []
        if not ns.prefix:
            continue
        ns.resources.append(
            Resource(
                id=None,
                name=f"{ns.prefix} through OLS",
                description=f"{ns.prefix} through OLS",
                mirId=None,
                sampleId=None,
                resourceHomeUrl=None,
                urlPattern=f"https://www.ebi.ac.uk/ols4/ontologies/{ns.prefix}/terms?obo_id={ns.prefix.upper()}"
                + ":{$id}",
                **ols_info,
            )
        )

    return {ns.prefix: ns for ns in namespaces}  # type: ignore


def misc_namespaces() -> Dict[str, Namespace]:
    """Define misc namespaces."""
    namespaces = [
        Namespace(
            id="brenda.ligand",
            pattern=r"^\d+$",
            name="BRENDA Ligand",
            prefix=None,
            description="BRENDA Ligand Information",
            namespaceEmbeddedInLui=False,
        ),
        Namespace(
            id="metabolights.compound",
            pattern=r"^MTBLC\d+$",
            name="Metabolights compound",
            prefix=None,
            description="metabolights compound",
            namespaceEmbeddedInLui=False,
        ),
    ]

    return {ns.id: ns for ns in namespaces}  # type: ignore


class Registry:
    """Managing the available annotation information.

    Registry of meta information.
    """

    URL = "https://registry.api.identifiers.org/resolutionApi/getResolverDataset"
    CUSTOM_NAMESPACES = {
        **ols_namespaces(),
        **misc_namespaces(),
    }

    def __init__(
        self,
        cache_duration: int = 24,
        cache: bool = True,
    ):
        """Initialize registry.

        :param cache_path: Path of cached identifiers.org path
        :param cache_duration: Duration of caching in hours.
        :param cache: boolean flag to stop caching
        """
        self.registry_path = pymetadata.CACHE_PATH / "identifiers_registry.json"

        # check if update needed
        if cache:
            if os.path.exists(self.registry_path):
                registry_age = (
                    time.time() - os.path.getmtime(self.registry_path)
                ) / 3600  # [hr]
                update = registry_age > cache_duration
            else:
                update = True
        else:
            update = True

        self.ns_dict: Dict[str, Namespace] = (
            self.update() if update else Registry.load_registry(self.registry_path)
        )

    def update(self) -> Dict[str, Namespace]:
        """Update registry."""
        Registry.update_registry(registry_path=self.registry_path)
        return Registry.load_registry(registry_path=self.registry_path)

    @staticmethod
    def update_registry(
        custom_namespaces: Dict[str, Namespace] = CUSTOM_NAMESPACES,
        registry_path: Optional[Path] = None,
    ) -> Dict[str, Namespace]:
        """Update registry from identifiers.org webservice."""
        logger.info(f"Update registry from '{Registry.URL}'")
        response = requests.get(Registry.URL)
        namespaces = response.json()["payload"]["namespaces"]

        ns_dict = {}
        for _, data in enumerate(namespaces):
            ns = Namespace.from_dict(data)
            ns_dict[ns.prefix] = ns

        if custom_namespaces is not None:
            for key, ns in custom_namespaces.items():
                if key in ns_dict:
                    logger.error(
                        f"Namespace with key '{key}' exists in MIRIAM. Overwrite namespace!"
                    )
                ns_dict[key] = ns

        if registry_path is not None:
            write_json_cache(
                data=ns_dict,
                cache_path=registry_path,
                json_encoder=DataclassJSONEncoder,
            )

        return ns_dict  # type: ignore

    @staticmethod
    def load_registry(registry_path: Path) -> Dict[str, Namespace]:
        """Load namespaces with resources from path."""
        if not registry_path.exists():
            Registry.update_registry(registry_path=registry_path)

        d = read_json_cache(cache_path=registry_path)
        if not d:
            raise ValueError("Registry could not be loaded from cache.")

        return {k: Namespace(**v) for k, v in d.items()}


REGISTRY = Registry()

if __name__ == "__main__":
    registry = Registry(cache=False)
    console.print(registry.ns_dict)
