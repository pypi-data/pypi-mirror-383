from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Owner:
    firstName: str
    lastName: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "firstName": self.firstName,
            "lastName": self.lastName,
        }

@dataclass
class IbanInfo:
    bank: str
    depositNumber: str
    iban: str
    status: str
    owners: List[Owner]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bank": self.bank,
            "depositNumber": self.depositNumber,
            "iban": self.iban,
            "status": self.status,
            "owners": [ o.to_dict() for o in self.owners ],
        }

@dataclass
class JibitCard:
    number: str
    type: str
    ibanInfo: IbanInfo

    def to_dict(self) -> Dict[str, Any]:
        return {
            "number": self.number,
            "type": self.type,
            "ibanInfo": self.ibanInfo.to_dict(),
        }

@dataclass
class JibitTokens:
    access_token: str
    refresh_token: str

    def to_dict(self) -> Dict[str, Any]:
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
