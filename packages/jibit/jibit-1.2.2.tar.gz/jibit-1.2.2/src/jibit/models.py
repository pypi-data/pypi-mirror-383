from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


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

@dataclass
class AddressInfo:
    postal_code:Optional[str]
    address:Optional[str]
    province:Optional[str]
    district:Optional[str]
    street:Optional[str]
    no:Optional[str]
    floor:Optional[str]

@dataclass
class WgsInfo:
    postal_code:Optional[str]
    latitude:Optional[float]
    longitude:Optional[float]

@dataclass
class IdentitySimilarity:
    first_name_similarity_percentage:float
    last_name_similarity_percentage:float
    full_name_similarity_sercentage:float
    father_name_similarity_percentage:float

@dataclass
class IdentificationDocument:
    type:str
    code:str
    issue_date:str
    expiration_date:str

@dataclass
class ForeignerIdentityInfo:
    fida:str
    first_name:str
    last_name:str
    father_name:str
    birth_date:str
    ancestor_name:str
    gender:str
    birth_place_country:str
    birth_place_city:str
    nationality:str
    identification_documents:List[IdentificationDocument]

@dataclass
class CorporationIdentityInfo:
    lic_issue_date:str
    lic_expire_date:str
    lic_type:str
    lic_time:str
    address:str
    blue_plaque:str
    registered_plaque:str
    postal_code:str
    area:str
    union_name:str
    union_id:str
    guild_id:str
    convent_id:str
    convent_name:str
    city_id:str
    board_title:str
    corporate_identity:str
    lic_state:str
    tel:str
    isic:str
    isic_name:str
    company_nationalCode:str
    hcLicense_request_type_name:str
    has_expire_letter:str
    expire_letter_date:str
    code:str
    first_name:str
    last_name:str
    father_name:str
    national_code:str
    is_male:str
    mobile:str
    type_name:str
    type_code:str
    birth_date:str
    identity_no:str
    country:str
    religion:str
    military_state:str
    education_level:str
    provider_tracker_id:str


@dataclass
class militaryServiceQualificationInfo:
    national_code:str
    qualified:bool
    description:str
    provider_tracker_id:str

@dataclass
class SanaInfo:
    national_code:str
    mobile_number:str
    registered:bool
    matched:bool

class BankIdentify(str,Enum):
    MARKAZI = ('MARKAZI', 'https://www.cbi.ir/')
    SANAT_VA_MADAN = ('SANAT_VA_MADAN', 'https://www.bim.ir/')
    MELLAT = ('MELLAT', 'https://www.bankmellat.ir/')
    REFAH = ('REFAH', 'https://www.refah-bank.ir/')
    MASKAN = ('MASKAN', 'https://www.bank-maskan.ir/')
    SEPAH = ('SEPAH', 'https://www.banksepah.ir/')
    KESHAVARZI = ('KESHAVARZI', 'https://www.bki.ir/')
    MELLI = ('MELLI', 'https://www.bmi.ir/')
    TEJARAT = ('TEJARAT', 'https://www.tejaratbank.ir/')
    SADERAT = ('SADERAT', 'https://www.bsi.ir/')
    TOSEAH_SADERAT = ('TOSEAH_SADERAT', 'https://www.edbi.ir/')
    POST = ('POST', 'https://www.postbank.ir/')
    TOSEAH_TAAVON = ('TOSEAH_TAAVON', 'https://www.ttbank.ir/')
    KARAFARIN = ('KARAFARIN', 'https://www.karafarinbank.ir/')
    PARSIAN = ('PARSIAN', 'https://www.parsian-bank.ir/')
    EGHTESAD_NOVIN = ('EGHTESAD_NOVIN', 'https://www.enbank.ir/')
    SAMAN = ('SAMAN', 'https://www.sb24.ir/')
    PASARGAD = ('PASARGAD', 'https://www.bpi.ir/')
    SARAYMEH = ('SARMAYEH', 'https://www.sbank.ir/')
    SINA = ('SINA', 'https://www.sinabank.ir/')
    MEHR_IRAN = ('MEHR_IRAN', 'https://www.qmb.ir/')
    SHAHR = ('SHAHR', 'https://www.shahr-bank.ir/')
    AYANDEH = ('AYANDEH', 'https://www.ba24.ir/')
    GARDESHGARI = ('GARDESHGARI', 'https://www.tourismbank.ir/')
    DAY = ('DAY', 'https://www.bank-day.ir/')
    IRANZAMIN = ('IRANZAMIN', 'https://www.izbank.ir/')
    RESALAT = ('RESALAT', 'https://www.rqbank.ir/')
    MELAL = ('MELAL', 'https://www.melalbank.ir/')
    KHAVARMIANEH = ('KHAVARMIANEH', 'https://www.middleeastbank.ir/')
    NOOR = ('NOOR', 'http://www.noorbank.ir/')
    IRAN_VENEZUELA = ('IRAN_VENEZUELA', 'http://www.ivbb.ir/')

    def __new__(cls, code, website):
        obj = str.__new__(cls, website)
        obj._value_ = code
        obj._website_ = website
        return obj

    @property
    def website(self):
        return self._website_

@dataclass
class Balance:
    balance_type:str
    currency:str
    amount:int


