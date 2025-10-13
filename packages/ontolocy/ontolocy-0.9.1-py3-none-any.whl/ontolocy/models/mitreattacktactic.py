from datetime import datetime
from typing import ClassVar, Optional

from pydantic import HttpUrl, StringConstraints, field_serializer
from typing_extensions import Annotated

from ..node import OntolocyNode
from ..relationship import OntolocyRelationship
from .mitreattacktechnique import MitreAttackTechnique


class MitreAttackTactic(OntolocyNode):
    __primaryproperty__: ClassVar[str] = "stix_id"
    __primarylabel__: ClassVar[str] = "MitreAttackTactic"

    stix_id: str
    stix_type: str
    stix_created: datetime
    stix_modified: datetime
    stix_spec_version: str = "2.1"
    stix_revoked: Optional[bool] = False

    attack_id: Annotated[str, StringConstraints(to_upper=True, pattern=r"TA\d{4}")]  # noqa: F722
    attack_spec_version: str
    attack_version: str
    attack_shortname: str
    attack_deprecated: Optional[bool] = False

    ref_url: HttpUrl
    name: str
    description: str

    @field_serializer("ref_url")
    def serialize_ref_url(self, ref_url: HttpUrl, _info):
        return str(ref_url)

    def __str__(self) -> str:
        return f"{self.attack_id}: {self.name}"


#
# OUTGOING RELATIONSHIPS
#


class MitreTacticIncludesTechnique(OntolocyRelationship):
    source: MitreAttackTactic
    target: MitreAttackTechnique

    __relationshiptype__: ClassVar[str] = "MITRE_TACTIC_INCLUDES_TECHNIQUE"
