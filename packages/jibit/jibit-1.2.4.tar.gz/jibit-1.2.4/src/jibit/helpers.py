from typing import List

from .models import JibitCard, Owner, IbanInfo, AddressInfo, WgsInfo, IdentitySimilarity, ForeignerIdentityInfo, \
    IdentificationDocument, CorporationIdentityInfo, militaryServiceQualificationInfo, SanaInfo, Balance


def parse_card_shaba_response(data: dict) -> JibitCard:
    owners = [Owner(**o) for o in data["ibanInfo"]["owners"]]
    iban_info = IbanInfo(
        bank=data["ibanInfo"]["bank"],
        depositNumber=data["ibanInfo"]["depositNumber"],
        iban=data["ibanInfo"]["iban"],
        status=data["ibanInfo"]["status"],
        owners=owners
    )
    return JibitCard(number=data["number"], type=data["type"], ibanInfo=iban_info)

def parse_postal_to_address_response(data: dict) -> AddressInfo:
    return AddressInfo(
        postal_code=data.get('postalCode'),
        address=data.get('address'),
        province=data.get('Province'),
        district=data.get('district'),
        street=data.get('street'),
        no=data.get('no'),
        floor=data.get('floor'),
    )

def parse_postal_wsginfo_response(data: dict) -> WgsInfo:
    return WgsInfo(
        postal_code=data.get('postalCode'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
    )

def parse_identity_similarity_response(data: dict) -> IdentitySimilarity:
    return IdentitySimilarity(
        first_name_similarity_percentage=data.get('firstNameSimilarityPercentage'),
        last_name_similarity_percentage=data.get('lastNameSimilarityPercentage'),
        full_name_similarity_sercentage=data.get('fullNameSimilarityPercentage'),
        father_name_similarity_percentage=data.get('fatherNameSimilarityPercentage'),
    )

def parse_identity_foreigners_response(data: dict) -> ForeignerIdentityInfo:
    identification_documents = data.get('identification_documents')
    return ForeignerIdentityInfo(
        fida=data.get('fida'),
        first_name=data.get('firstName'),
        last_name=data.get('lastName'),
        father_name=data.get('fatherName'),
        birth_date=data.get('birthDate'),
        ancestor_name=data.get('ancestorName'),
        gender=data.get('gender'),
        birth_place_country=data.get('birthPlaceCountry'),
        birth_place_city=data.get('birthPlaceCity'),
        nationality=data.get('nationality'),
        identification_documents=[
            IdentificationDocument(
                type=i.get('type'),
                code=i.get('code'),
                issue_date=i.get('issue_date'),
                expiration_date=i.get('expiration_date')
            ) for i in identification_documents
        ]
    )


def parse_identity_corporation_response(data: dict) -> CorporationIdentityInfo:
    return CorporationIdentityInfo(
        lic_issue_date=data.get("licIssueDate", ""),
        lic_expire_date=data.get("licExpireDate", ""),
        lic_type=data.get("licType", ""),
        lic_time=data.get("licTime", ""),
        address=data.get("address", ""),
        blue_plaque=data.get("bluePlaque", ""),
        registered_plaque=data.get("registeredPlaque", ""),
        postal_code=data.get("postalCode", ""),
        area=str(data.get("area", "")),
        union_name=data.get("unionName", ""),
        union_id=str(data.get("unionId", "")),
        guild_id=str(data.get("guildId", "")),
        convent_id=str(data.get("conventId", "")),
        convent_name=data.get("conventName", ""),
        city_id=str(data.get("cityId", "")),
        board_title=data.get("boardTitle", ""),
        corporate_identity=data.get("corporateIdentity", ""),
        lic_state=data.get("licState", ""),
        tel=data.get("tel", ""),
        isic=data.get("isic", ""),
        isic_name=data.get("isicName", ""),
        company_nationalCode=data.get("companyNationalCode", ""),
        hcLicense_request_type_name=data.get("hcLicenseRequestTypeName", ""),
        has_expire_letter=data.get("hasExpireLetter", ""),
        expire_letter_date=data.get("expireLetterDate", ""),
        code=data.get("code", ""),
        first_name=data.get("firstName", ""),
        last_name=data.get("lastName", ""),
        father_name=data.get("fatherName", ""),
        national_code=data.get("nationalCode", ""),
        is_male=data.get("isMale", ""),
        mobile=data.get("mobile", ""),
        type_name=data.get("typeName", ""),
        type_code=data.get("typeCode", ""),
        birth_date=data.get("birthDate", ""),
        identity_no=data.get("identityNo", ""),
        country=data.get("country", ""),
        religion=data.get("religion", ""),
        military_state=data.get("militaryState", ""),
        education_level=data.get("educationLevel", ""),
        provider_tracker_id=data.get("providerTrackerId", "")
    )


def parse_military_qualification_info(data:dict)->militaryServiceQualificationInfo:
    return militaryServiceQualificationInfo(
        national_code=data['nationalCode'],
        qualified=data['qualified'],
        description=data['description'],
        provider_tracker_id=data['providerTrackerId']
    )

def parse_sana_info(data:dict)->SanaInfo:
    return SanaInfo(
        national_code=data['nationalCode'],
        mobile_number=data['mobileNumber'],
        registered=data['registered'],
        matched=data['matched']
    )

def parse_balances(data:dict)->List[Balance]:
    return [
        Balance(
            balance_type=d['balanceType'],
            currency=d['currency'],
            amount=d['amount'],
        )
        for d in data
    ]