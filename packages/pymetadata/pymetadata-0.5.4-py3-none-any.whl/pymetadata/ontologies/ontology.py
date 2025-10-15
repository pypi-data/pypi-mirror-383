"""Ontology support.

This file allows to download the ontologies for local use.
Special ontologies are provided as enums.

Uses the OWL links provided on OLS4 to download the ontologies.
"""

import gzip
import importlib
import re
import shutil
import tempfile
import warnings
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pronto
import requests
from jinja2 import Template
from pronto.ontology import Ontology as ProntoOntology
from pronto.relationship import Relationship as ProntoRelationship
from pronto.term import Term as ProntoTerm

from pymetadata import ENUM_DIR, RESOURCES_DIR, log
from pymetadata.console import console

logger = log.get_logger(__name__)


class OntologyFormat(str, Enum):
    """Formats for ontologies."""

    OBO = "obo"
    OWL = "owl"


@dataclass
class OntologyFile:
    """Definition file for ontology."""

    id: str
    name: str
    format: OntologyFormat
    source: str
    bioportal: bool
    ols: bool

    @property
    def path(self) -> Path:
        """Path of ontology file."""
        return RESOURCES_DIR / "ontologies" / f"{self.id.lower()}.{self.format.value}.gz"

    @property
    def filename(self) -> str:
        """Filename of ontology file.

        :return: ontology filename
        :rtype: str
        """
        name = str(self.path)
        console.print(name)
        return name


_ontology_files: List[OntologyFile] = [
    OntologyFile(
        "BTO",
        name="The BRENDA Tissue Ontology (BTO)",
        format=OntologyFormat.OWL,
        source="http://purl.obolibrary.org/obo/bto.owl",
        bioportal=False,
        ols=True,
    ),
    OntologyFile(
        "CHEBI",
        name="Chemical Entities of Biological Interest Ontology",
        format=OntologyFormat.OWL,
        source="http://purl.obolibrary.org/obo/chebi.owl",
        bioportal=True,
        ols=True,
    ),
    OntologyFile(
        "FMA",
        name="Foundational Model of Anatomy",
        format=OntologyFormat.OWL,
        source="http://purl.obolibrary.org/obo/fma.owl",
        bioportal=True,
        ols=True,
    ),
    OntologyFile(
        "ECO",
        name="Evidence & Conclusion Ontology (ECO)",
        format=OntologyFormat.OWL,
        source="http://purl.obolibrary.org/obo/eco.owl",
        bioportal=True,
        ols=True,
    ),
    OntologyFile(
        "GO",
        name="Gene Ontology",
        format=OntologyFormat.OWL,
        source="http://purl.obolibrary.org/obo/go/extensions/go-plus.owl",
        bioportal=True,
        ols=True,
    ),
    OntologyFile(
        "KISAO",
        name="Kinetic Simulation Algorithm Ontology",
        format=OntologyFormat.OWL,
        # source="https://raw.githubusercontent.com/SED-ML/KiSAO/deploy/kisao.owl",
        source="https://raw.githubusercontent.com/SED-ML/KiSAO/dev/kisao.owl",
        bioportal=True,
        ols=True,
    ),
    OntologyFile(
        "SBO",
        name="Systems Biology Ontology",
        format=OntologyFormat.OWL,
        source="https://raw.githubusercontent.com/EBI-BioModels/SBO/master/SBO_OWL.owl",
        bioportal=True,
        ols=True,
    ),
    OntologyFile(
        "NCIT",
        name="National Cancer Institute Thesaurus",
        format=OntologyFormat.OWL,
        source="http://purl.obolibrary.org/obo/ncit.owl",
        bioportal=True,
        ols=True,
    ),
    #     OntologyFile(
    #     "NCBITAXON",
    #     name="NCBI organismal classification",
    #     format=OntologyFormat.OWL,
    #     source=OLS_BASE_URL + "ncbitaxon",
    #     bioportal=False,
    #     ols=True,
    # ),
]


ontology_files: Dict[str, OntologyFile] = {
    ontology.id: ontology for ontology in _ontology_files
}


def update_ontology_file(ofile: OntologyFile) -> None:
    """Download latest versions of ontologies."""

    oid = ofile.id

    logger.info(f"Update ontology: `{oid}`")

    with tempfile.TemporaryDirectory() as tmp_dir:
        # download in tmp location
        owl_path = Path(tmp_dir) / f"{oid.lower()}.owl"
        url = ofile.source
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(owl_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # only store gzip version
        with open(owl_path, "rb") as f_in:
            gzip_path = RESOURCES_DIR / "ontologies" / f"{oid.lower()}.owl.gz"
            with gzip.open(gzip_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)


def update_ontology_files() -> None:
    """Download latest ontology files."""
    with ThreadPoolExecutor(max_workers=4) as pool:
        for ofile in ontology_files.values():
            pool.submit(update_ontology_file, ofile)


class Ontology:
    """Ontology."""

    _ontology: Optional[ProntoOntology] = None

    def __init__(self, ontology_id: str):
        """Construct ontology."""
        ontology_file = ontology_files[ontology_id]
        logger.info(f"Read ontology: `{ontology_id}`")

        # read ontology with pronto
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", pronto.utils.warnings.SyntaxWarning)
            warnings.simplefilter("ignore", pronto.utils.warnings.NotImplementedWarning)
            self.__class__._ontology = pronto.Ontology(ontology_file.filename)

    def get_pronto_ontology(self) -> Optional[ProntoOntology]:
        """Get a proto object for the ontology.

        :return: `pronto.Ontology`: pronto object for the ontology
        :rtype: [type]
        """
        return self._ontology


def create_ontology_enum(ontology_id: str, pattern: str) -> None:
    """Create enum of the ontology."""

    logger.info(f"Create enum: `{ontology_id}`")

    def name_to_variable(name: str) -> Optional[str]:
        """Clean string to python variable name."""
        if name is None:
            return None
        name = re.sub(r"\W|^(?=\d)", "_", name)
        return name.upper()

    # load ontology
    terms: Dict[str, Dict] = {}
    ontology: Ontology = Ontology(ontology_id=ontology_id)

    names = set()
    pronto_term: Union[ProntoTerm, ProntoRelationship]

    if not ontology._ontology:
        raise ValueError(f"No Pronto Ontology for `{ontology_id}`")

    for term_id in ontology._ontology:
        pronto_term = ontology._ontology[term_id]

        pronto_name: Union[str, None, Any] = pronto_term.name
        if not isinstance(pronto_name, str):
            logger.warning(f"Pronto name is none: `{pronto_term}`")
            continue

        var_name: Optional[str] = name_to_variable(pronto_name)
        if var_name in names:
            logger.error(f"Duplicate name in ontology: `{var_name}`")
            continue
        else:
            names.add(var_name)
            term_id = pronto_term.id
            # fix the ids
            if ontology_id == "KISAO":
                term_id = term_id.replace("http://www.biomodels.net/kisao/KISAO#", "")
            if ontology_id == "SBO":
                term_id = term_id.replace("http://biomodels.net/SBO/", "")

            if ":" in term_id:
                term_id = term_id.replace(":", "_")

            terms[term_id] = {
                "id": term_id,
                "var_name": var_name,
                "name": pronto_name.replace('"', "'"),
                "definition": pronto_term.definition,
            }
    terms_sorted = {}
    for key in sorted(terms.keys()):
        terms_sorted[key] = terms[key]

    with open(
        RESOURCES_DIR / "templates" / "ontology_enum.pytemplate", "r"
    ) as f_template:
        template = Template(
            f_template.read(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        context = {
            "ontology_id": ontology_id,
            "terms": terms_sorted,
            "pattern": pattern,
        }
        module_str = template.render(**context)
        # print(module_str)
        path_module = ENUM_DIR / f"{ontology_id.lower()}.py"
        print(path_module)
        with open(path_module, "w") as f_py:
            f_py.write(module_str)


def try_ontology_import(ontology_id: str) -> None:
    """Try import of created module."""
    # try to import
    importlib.import_module(f"pymetadata.metadata.{ontology_id.lower()}")


if __name__ == "__main__":
    # download latest versions
    update_ontology_files()

    # test loading of OWL files
    # ofile: OntologyFile
    # for oid, ofile in ontology_files.items():
    #     console.rule(style="white")
    #     ontology = Ontology(ontology_id=oid)
    #     console.print(ontology)
    # ontology = Ontology(ontology_id="CHEBI")

    # convert to python module
    create_ontology_enum("SBO", r"^SBO_\d{7}$")
    create_ontology_enum("KISAO", r"^KISAO_\d{7}$")
    create_ontology_enum("ECO", r"^ECO_\d{7}$")

    try_ontology_import("SBO")
    try_ontology_import("KISAO")
    try_ontology_import("ECO")

    # for ontology_id in ontology_files:
    #     create_ontology_enum(ontology_id)
