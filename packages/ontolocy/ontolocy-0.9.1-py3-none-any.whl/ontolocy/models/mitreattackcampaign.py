from datetime import datetime
from typing import ClassVar, Optional

from pydantic import HttpUrl, field_serializer

from ..node import OntolocyNode
from ..relationship import OntolocyRelationship
from .intrusionset import IntrusionSet
from .mitreattacksoftware import MitreAttackSoftware
from .mitreattacktechnique import MitreAttackTechnique


class MitreAttackCampaign(OntolocyNode):
    __primaryproperty__: ClassVar[str] = "stix_id"
    __primarylabel__: ClassVar[str] = "MitreAttackCampaign"

    stix_id: str
    stix_type: str
    stix_created: datetime
    stix_modified: datetime
    stix_spec_version: str = "2.1"
    stix_revoked: Optional[bool] = False
    stix_first_seen: datetime
    stix_last_seen: datetime

    attack_spec_version: str
    attack_version: str
    attack_first_seen_citation: str
    attack_last_seen_citation: str
    attack_id: str
    attack_deprecated: Optional[bool] = False

    ref_url: HttpUrl
    name: str
    description: str

    @field_serializer("ref_url")
    def serialize_ref_url(self, ref_url: HttpUrl, _info):
        return str(ref_url)


#
# OUTGOING RELATIONSHIPS
#


class MitreCampaignUsesTechnique(OntolocyRelationship):
    source: MitreAttackCampaign
    target: MitreAttackTechnique

    __relationshiptype__: ClassVar[str] = "MITRE_CAMPAIGN_USES_TECHNIQUE"


class MitreCampaignUsesSoftware(OntolocyRelationship):
    source: MitreAttackCampaign
    target: MitreAttackSoftware

    __relationshiptype__: ClassVar[str] = "MITRE_CAMPAIGN_USES_SOFTWARE"


class MitreCampaignAttributedTo(OntolocyRelationship):
    source: MitreAttackCampaign
    target: IntrusionSet

    __relationshiptype__: ClassVar[str] = "MITRE_CAMPAIGN_ATTRIBUTED_TO_INTRUSION_SET"
