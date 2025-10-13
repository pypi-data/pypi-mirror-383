# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["InflationListAvailableResponse"]


class InflationListAvailableResponse(BaseModel):
    countries: Optional[List[str]] = None
    """
    Lista de nomes de países (em minúsculas) para os quais há dados de inflação
    disponíveis (ex: `brazil`, `usa`, `argentina`).
    """
