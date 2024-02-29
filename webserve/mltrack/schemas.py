from ninja.orm import create_schema

from mltrack.consumer_prompt_models import UserLevelVectorIndex


UserLevelVectorIndexSchema = create_schema(UserLevelVectorIndex, exclude=["embedding"])
