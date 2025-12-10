from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ExtractedLocations(BaseModel):
    """Structured information about travel locations."""
    origin: str = Field(...,
                        description="The starting city or location of the trip.")
    destination: str = Field(...,
                             description="The final city or destination of the trip.")
    # --- ADD THIS ---
    duration_days: Optional[int] = Field(
        None, description="The duration of the trip in days, if mentioned.")
    # --- END ADDITION ---


class RankedAttraction(BaseModel):
    """A single ranked attraction with a justification."""
    name: str = Field(..., description="The name of the attraction.")
    reasoning: str = Field(...,
                           description="A brief explanation of why this matches, considering the trip duration."
                           )


class RankedAttractionsList(BaseModel):
    """A ranked list of the top attractions based on the user's query."""
    top_attractions: List[RankedAttraction] = Field(...,
                                                    description="A list of the top ranked attractions."
                                                    )


class GuardrailOutcome(BaseModel):
    """The classification of the user's query."""
    decision: Literal["valid", "incomplete", "unrelated", "greeting"] = Field(
        ...,
        description="The category of the query. 'valid' means it has origin, destination, AND duration."
    )
    feedback_message: str = Field(
        ...,
        description="A friendly response to the user. If valid, say 'Processing...'. If incomplete, ask for the missing info."
    )
