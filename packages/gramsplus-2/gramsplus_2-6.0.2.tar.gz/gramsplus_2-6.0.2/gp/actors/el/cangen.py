from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, Sequence

from gp.actors.data import KGDB, GPExample
from gp.actors.el.canreg import CanRegActor
from gp.entity_linking.candidate_generation.common import (
    CanEnt,
    CanGenBasicMethod,
    CanGenMethod,
    TableCanGenResult,
)
from gp.entity_linking.candidate_generation.oracle_model import CanGenOracleMethod
from gp.misc.appconfig import AppConfig
from libactor.actor import Actor
from libactor.cache import BackendFactory, IdentObj, cache, fmt_keys
from sm.dataset import Example, FullTable
from sm.misc.funcs import import_attr
from sm.namespaces.utils import KGName


@dataclass
class CanGenActorArgs:
    clspath: str | type
    clsargs: dict | object = field(default_factory=dict)
    # localsearch: Optional[LocalSearchArgs] = field(
    #     default=None,
    #     metadata={
    #         "help": "Search for more candidates by matching the entity's properties with the table's cells"
    #     },
    # )
    soft_limit: int = field(
        default=1000,
        metadata={"help": "The maximum number of candidates per query to be returned."},
    )
    add_gold: Literal["no", "when-not-topk", "always"] = field(
        default="no",
        metadata={
            "help": "add gold entities. options:"
            "- no: never"
            "- when-not-topk: when the gold entity is in candidate entities but not in the top k"
            "- always: add the gold entity when it's missing",
        },
    )


class CanGenActor(Actor[CanGenActorArgs]):
    """Generate candidate entities for cells in a table."""

    # VERSION = ActorVersion.create(100, [LocalSearch])
    VERSION = 102
    EXP_NAME = "Candidate Generation"
    EXP_VERSION = 3

    def __init__(
        self,
        params: CanGenActorArgs,
    ):
        super().__init__(params)

    def forward(
        self,
        example: IdentObj[Example[FullTable]],
        ent_cols: IdentObj[list[int]],
        kgdb: IdentObj[KGDB],
    ) -> IdentObj[TableCanGenResult]:
        value = self.invoke(example, ent_cols, kgdb)
        return IdentObj(
            key=fmt_keys(
                self.key,
                ex=example.key,
                entcols=ent_cols.key,
            ),
            value=value,
        )

    @cache(
        backend=BackendFactory.actor.sqlite.pickle(mem_persist=True),
    )
    def invoke(
        self,
        example: IdentObj[Example[FullTable]],
        ent_cols: IdentObj[list[int]],
        kgdb: IdentObj[KGDB],
    ) -> TableCanGenResult:
        res = self.get_method(kgdb).get_candidates([example.value], [ent_cols.value])[0]
        return self.fixed_redirections(
            kgdb.value, example.value.table.table.shape(), res
        )

    # @Cache.flat_cache(
    #     backend=Cache.sqlite.serde(
    #         cls=TableCanGenResult, filename="cangen", mem_persist=True
    #     ),
    #     cache_key=lambda self, example, verbose=False: example.id,
    #     disable=lambda self: not AppConfig.get_instance().is_cache_enable,
    # )
    # def batch_call(
    #     self, examples: Sequence[GPExample], verbose: bool = False
    # ) -> list[TableCanGenResult]:
    #     if len(examples) == 0:
    #         return []

    #     kgname = examples[0].kgname
    #     assert all(ex.kgname == kgname for ex in examples)

    #     ent_cols = [self.canreg_actor(ex) for ex in examples]
    #     return [
    #         self.fixed_redirections(kgname, examples[ei].table.table.shape(), res)
    #         for ei, res in enumerate(
    #             self.get_method(kgname).get_candidates(
    #                 examples, ent_cols, verbose=verbose
    #             )
    #         )
    #     ]

    # def get_candidate_entities(
    #     self, examples: list[GPExample]
    # ) -> list[TableCanGenResult]:
    #     return self.batch_call(examples)

    def fixed_redirections(
        self, kgdb: KGDB, shp: tuple[int, int], res: TableCanGenResult
    ) -> TableCanGenResult:
        ent_redirections = kgdb.pydb.entity_redirections.cache()

        if any(id in ent_redirections for id in res.ent_id):
            res = TableCanGenResult.from_matrix(
                res.to_matrix(shp).map(
                    lambda lst: [
                        CanEnt(ent_redirections.get(x.id, x.id), x.score) for x in lst
                    ]
                )
            )
        return res

    # def is_oracle_entity_linking(self, kgname: KGName) -> bool:
    #     return isinstance(
    #         self.get_method(kgname), CanGenOracleMethod
    #     ) and self.canreg_actor.is_oracle_entity_linking(kgname)

    @cache(backend=BackendFactory.actor.mem)
    def get_method(self, kgdb: IdentObj[KGDB]) -> CanGenMethod:
        if isinstance(self.params.clspath, str):
            cls = import_attr(self.params.clspath)
        else:
            cls = self.params.clspath

        if issubclass(cls, CanGenBasicMethod):
            return cls(kgdb.value, self.params.clsargs)
        if isinstance(self.params.clsargs, dict):
            return cls(**self.params.clsargs)
        return cls(self.params.clsargs)

    # @Cache.cache(
    #     backend=Cache.cls.dir(
    #         cls=DatasetCandidateEntities, mem_persist=True, log_serde_time=True
    #     ),
    #     disable=lambda self: not AppConfig.get_instance().is_cache_enable,
    # )
    # def __call__(self, dsquery: str) -> DatasetCandidateEntities:
    #     examples = self.data_actor(dsquery)
    #     entity_columns = self.canreg_actor(dsquery)

    #     cans = self.method(DatasetQuery.from_string(dsquery).dataset).get_candidates(
    #         dsquery, examples, entity_columns
    #     )

    #     # TODO: this is a special hack for the experiments that we do not want to
    #     # mess up the previous cache as we are limited in time and cannot re-compute the
    #     # ranking

    #     # we want to add the gold entity to the candidates if it's not there.
    #     if self.params.soft_limit == 99:
    #         # add if it's not in the top 100
    #         self.logger.warning(
    #             "We are adding gold entities to the candidates. You should know what you are doing!"
    #         )
    #         gold_ents: dict[str, dict[int, dict[int, list[CandidateEntity]]]] = (
    #             defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    #         )
    #         db = self.data_actor.get_kgdb(dsquery).pydb

    #         entity_metadata = db.entity_metadata.cache()
    #         entity_pagerank = db.entity_pagerank.cache()

    #         for ex in examples:
    #             table_id = ex.table.table.table_id
    #             for ri, ci, links in ex.table.links.enumerate_flat_iter():
    #                 if len(links) > 0:
    #                     for link in links:
    #                         for entity_id in link.entities:
    #                             entity_id = str(entity_id)
    #                             ent = entity_metadata[entity_id]
    #                             gold_ents[table_id][ci][ri].append(
    #                                 CandidateEntity(
    #                                     id=ent.id,
    #                                     label=str(ent.label),
    #                                     description=str(ent.description),
    #                                     aliases=sorted(ent.aliases.get_all()),
    #                                     popularity=entity_pagerank[ent.id],
    #                                     score=0.0,
    #                                 )
    #                             )
    #         cans = cans.top_k_candidates(self.params.soft_limit, gold_ents)

    #     if self.params.localsearch is not None:
    #         cans = LocalSearch(
    #             self.params.localsearch, self.data_actor.get_kgdb(dsquery)
    #         ).augment_candidates(examples, cans)
    #     return cans
