from gino import Gino
from gino.schema import GinoSchemaVisitor

from data.config import POSTGRESURI
import logging
logging.basicConfig()
logging.getLogger('gino.engine._SAEngine').setLevel(logging.ERROR)
db = Gino()

async def create_db():
    print(POSTGRESURI)
    await db.set_bind(POSTGRESURI, echo=False)
    db.gino: GinoSchemaVisitor
    await db.gino.create_all()