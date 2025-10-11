import os

from playhouse.sqlite_ext import CharField, FTSModel, IntegerField, SearchField

import sanguine.constants as c
from sanguine.db import db

type_to_id = {c.ENTITY_VARIABLE: 1, c.ENTITY_FUNCTION: 2, c.ENTITY_CLASS: 3}
id_to_type = {v: k for k, v in type_to_id.items()}


class CodeEntity(FTSModel):
    type = IntegerField()
    file = SearchField()
    name = SearchField()

    class Meta:
        database = db
