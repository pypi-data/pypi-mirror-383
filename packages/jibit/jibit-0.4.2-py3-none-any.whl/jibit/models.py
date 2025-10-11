from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Owner:
    firstName: str
    lastName: str

@dataclass
class IbanInfo:
    bank: str
    depositNumber: str
    iban: str
    status: str
    owners: List[Owner]

@dataclass
class Card:
    number: str
    type: str
    ibanInfo: IbanInfo

@dataclass
class JibitTokens:
    access_token: str
    refresh_token: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert tokens to a dictionary."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JibitTokens":
        """Create a JibitTokens instance from a dictionary."""
        return cls(
            access_token=data.get("access_token") or data.get("accessToken"),
            refresh_token=data.get("refresh_token") or data.get("refreshToken"),
        )
