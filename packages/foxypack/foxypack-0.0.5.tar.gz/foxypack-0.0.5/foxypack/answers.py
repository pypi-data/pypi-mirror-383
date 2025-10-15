from pydantic import BaseModel


class AnswersAnalysis(BaseModel):
    answer_id: str
    url: str
    social_platform: str
    type_content: str


class AnswersStatistics(BaseModel):
    answer_id: str
