from pydantic import BaseModel

class Service(BaseModel):
    service: str
    lastCollected: str
    nextCollection: str
    frequency: str
    binDescription: str
    wasteType: str
    collectedBy: str