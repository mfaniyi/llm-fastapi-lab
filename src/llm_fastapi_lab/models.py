from pydantic import BaseModel


class CandidateExtraction(BaseModel):
    name: str
    role: str
    experience_years: int