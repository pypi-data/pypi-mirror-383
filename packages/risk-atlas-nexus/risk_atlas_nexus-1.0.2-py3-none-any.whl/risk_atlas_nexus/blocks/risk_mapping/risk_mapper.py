import datetime
import json
import re
from typing import List

from sssom_schema import EntityReference, Mapping
from txtai import Embeddings

from risk_atlas_nexus.ai_risk_ontology.datamodel.ai_risk_ontology import Risk
from risk_atlas_nexus.blocks.inference import InferenceEngine
from risk_atlas_nexus.blocks.inference.params import TextGenerationInferenceOutput
from risk_atlas_nexus.blocks.prompt_builder import ZeroShotPromptBuilder
from risk_atlas_nexus.blocks.prompt_response_schema import LIST_OF_STR_SCHEMA
from risk_atlas_nexus.blocks.prompt_templates import RISK_IDENTIFICATION_TEMPLATE
from risk_atlas_nexus.blocks.risk_detector import GenericRiskDetector
from risk_atlas_nexus.blocks.risk_mapping import RiskMappingBase
from risk_atlas_nexus.metadata_base import MappingMethod


class RiskMapper(RiskMappingBase):

    def _bucket_semantic_score(self, score: int):
        """A simplistic method to bucket the scores

        Args:
            score: int
                The semantic score to be processed

        Returns:
            str
                A representation of the relationship
        """
        relationship = "noMatch"
        if score == 100:
            relationship = "skos:exactMatch"
        elif (score <= 100) and (score > 80):
            relationship = "skos:closeMatch"
        elif (score <= 80) and (score > 20):
            relationship = "skos:relatedMatch"

        return relationship

    def _format_with_curie(self, curie_prefix, entity_id):
        """Format the string with curie prefix

        Args:
            curie_prefix: str
                The curie prefix
            entity_id: str
                The linkml instance id

        Returns:
            EntityReference
                A formatted string
        """
        s = curie_prefix.strip() + ":" + entity_id.strip()
        return EntityReference(s)

    def generate(
        self,
        new_risks: list[Risk],
        existing_risks: list[Risk],
        inference_engine: InferenceEngine,
        new_prefix: str,
        mapping_method: MappingMethod,
    ) -> list[Mapping]:
        """Generate a list of mappings between two lists of risks
        Args:
            new_risks: list[Risk]
                A new set of risks
            existing_risks: list[Risk],
                Secondary list, this should be the list of existing risks in RAN
            inference_engine: (Optional)Union[InferenceEngine | None]:
                An LLM inference engine to infer risks from the usecases.
            new_prefix: str
                A curie prefix for the new list
            mapping_method: MappingMethod
                The method to generate the mapping

        Returns:
            list[Mapping]
        """
        mappings = []

        data = []
        taxonomy_for_mapping = {}
        for risk in existing_risks:
            # this embedding is just using name and description, not any other attributes
            data.append(
                "ID: "
                + risk.id
                + ", Name: "
                + risk.name
                + ", Description: "
                + risk.description
            )
            taxonomy_for_mapping[risk.id] = risk.isDefinedByTaxonomy

        if mapping_method == MappingMethod.SEMANTIC:
            # create an embedding with existing risk data

            embeddings = Embeddings(path="sentence-transformers/nli-mpnet-base-v2")
            embeddings.index(data)

            # Run an embeddings search for each new risk
            for nr in new_risks:
                # Extract uid of first result
                # search result format: (uid, score)
                query = (
                    "ID: "
                    + nr.id
                    + ", Name: "
                    + nr.name
                    + ", Description: "
                    + nr.description
                )

                # embedding search returns list of (id, score) for index search, e.g. [(54, 0.6546236872673035), (48, 0.5914335250854492)]
                # let's just use the top match for now

                top_result = embeddings.search(query, 5)[0][0]  # id of top result
                s = data[top_result]  # string data belonging to that ID
                result_id = re.search("ID:(.*), Name", s)
                result_name = re.search("Name:(.*), Description:", s)

                mapping = Mapping(
                    subject_id=self._format_with_curie(nr.isDefinedByTaxonomy, nr.id),
                    subject_label=nr.name,
                    predicate_id=self._bucket_semantic_score(top_result),
                    object_id=self._format_with_curie(
                        taxonomy_for_mapping[result_id.group(1).strip()],
                        result_id.group(1),
                    ),
                    object_label=result_name.group(1),
                    mapping_justification="semapv:SemanticSimilarityThresholdMatching",
                    similarity_score=top_result,
                    mapping_date=datetime.date.today(),
                    author_id="Risk_Atlas_Nexus_System",
                    comment="Autogenerated via semantic similarity script",
                )
                mappings.append(mapping)

        elif mapping_method == MappingMethod.INFERENCE:
            # this query is just using name and description, not any other attributes
            usecases = [
                (
                    "ID: "
                    + nr.id
                    + ", Name: "
                    + nr.name
                    + ", Description: "
                    + nr.description
                )
                for nr in new_risks
            ]

            risk_detector = GenericRiskDetector(
                risks=existing_risks,
                inference_engine=self.inference_engine,
                cot_examples=None,
            )

            rls = risk_detector.detect(usecases)

            for (
                index,
                rl,
            ) in enumerate(rls):
                for risk in rl:
                    mapping = Mapping(
                        subject_id=self._format_with_curie(
                            new_risks[index].isDefinedByTaxonomy, new_risks[index].id
                        ),
                        subject_label=new_risks[index].name,
                        predicate_id="skos:relatedMatch",  #  opted for this here as there is no way to assess relatedness of match with current template
                        object_id=self._format_with_curie(
                            taxonomy_for_mapping[risk.id.strip()], risk.id
                        ),
                        object_label=risk.name,
                        mapping_justification="semapv:LLMBasedMatching",
                        mapping_date=datetime.date.today(),
                        author_id="Risk_Atlas_Nexus_System",
                        comment="Autogenerated via LLM based matching script",
                    )
                    mappings.append(mapping)

        return mappings
