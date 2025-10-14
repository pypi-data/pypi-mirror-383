from pydantic import BaseModel, Field


class SearchTokenParameters(BaseModel):
    symbol: str = Field(description="The token symbol")
    top_n: int = Field(description="max num of tokens to be returned", default=10)


class GetTokenLaunchStatusParameters(BaseModel):
    token_address: str = Field(description="The token address")
