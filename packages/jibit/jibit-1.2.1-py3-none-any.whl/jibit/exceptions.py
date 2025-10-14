from enum import Enum

class JibitErrorCode(str, Enum):

    # DEPOSIT
    DEPOSIT_NOT_VALID = ("deposit.not_valid", "شماره حساب نامعتبر است")
    # IBAN
    IBAN_IS_REQUIRED = ("iban.required_is", "شماره شبا الزامی است")
    IBAN_NOT_VALID = ("iban.valid_not", "شماره شبا معتبر نیست")
    IBAN_IS_NOT_MATCH = ("iban.is_not_matched", "شماره شبا تطابق ندارد")
    IBAN_PROVIDED = ("iban.provided", "بجای شماره حساب، شماره شبا وارد شده")
    IBAN_NOT_FOUND = ("iban.not_found", " شبا یافت نشد")
    IBAN_NOT_FOUND_OWNER = ("iban.not_found_owner", "دارنده شبا یافت نشد")
    # CARD
    CARD_PROVIDED = ("card_number.provided", "بجای شماره حساب، شماره کارت وارد شده")
    CARD_IS_EXPIRED = ("card.is_expired", "کارت منقضی شده است")
    CARD_NOT_ACTIVE = ("card.not_active", "کارت غیرفعال است")
    CARD_NOT_VALID = ("card.not_valid", "شماره کارت نامعتبر است")
    CARD_IS_REQUIRED = ("card.is_required", "شماره کارت الزامی است")
    CARD_REGISTERED_AS_LOST = ("card.registered_as_lost", "کارت به عنوان مفقودی ثبت شده است")
    CARD_REGISTERED_AS_STOLEN = ("card.registered_as_stolen", "کارت به عنوان سرقتی ثبت شده است")
    CARD_ACCOUNT_NUMBER_NOT_VALID = ("card.account_number_not_valid", "شماره حساب کارت معتبر نیست")
    CARD_OWNER_NOT_AUTHORIZED = ("card.owner_not_authorized", "دارنده کارت مجاز نیست")
    CARD_SOURCE_BANK_IS_NOT_ACTIVE = ("card.source_bank_is_not_active", "بانک صادرکننده کارت فعال نیست")
    CARD_BLACK_LISTED = ("card.black_listed", "کارت در لیست سیاه است")
    CARD_PROVIDER_IS_NOT_ACTIVE = ("card.provider_is_not_active", "سرویس کارت فعال نیست")
    # JIBIT
    FORBIDDEN = ("forbidden", "دسترسی غیرمجاز")
    UNAUTHORIZED = ("JIBIT_401_UNAUTHORIZED", "توکن معتبر نیست یا منقضی شده است")
    DAILY_LIMIT_REACHED = ("daily_limit.reached", "سقف روزانه تراکنش‌ها پر شده است")
    HANDLER_NOT_FOUND = ("handler.notـfound", "سازوکاری یافت نشد")
    SERVICE_UNAVAILABLE = ("JIBIT_503_UNAVAILABLE", "سرویس جی‌بيت در دسترس نیست")
    # POSTAL
    POSTAL_NOT_FOUND = ("postalCode.notـfound", "کد پستی یافت نشد")
    POSTAL_NOT_VALID = ("postalCode.not_valid", "کد پستی معتبر نیست")
    # Fida
    FIDA_IS_REQUIRED = ("fida.is_required", "شناسه فراگیر اجباری است")
    FIDA_NOT_VALID = ("fida.not_valid", "شناسه فراگیر نامعتبر است")
    FIDA_BLACK_LISTED = ("fida.black_listed", "استعلام شناسه فراگیر امکان پذیر نیست")
    # OTHER
    MOBILE_NOT_VALID = ("mobileNumber.not_valid", "شماره همراه معتبر نیست")
    BIRTHDATE_NOT_VALID = ("birthDate.not_valid", "تاریخ تولد معتبر نیست")
    PARAMETERS_NOT_ACCEPTABLE = ("parameters.not_acceptable", "پارامترهای ارسالی نامعتبر هستند")
    IDENTITY_INFO_NOT_FOUND = ("identity_info.not_found", "اطلاعات هویتی یافت نشد.")
    MATCHING_UNKNOWN = ("matching.unknown", "تطابق نامشخص")
    INVALID_REQUEST_BODY = ("invalid.request_body", "بدنه درخواست نامعتبر است")
    BALANCE_NOT_ENOUGH = ("balance.not_enough", "موجودی کافی نیست")
    PROVIDERS_NOT_AVAILABLE = ("providers.not_available", "سرویس‌دهنده در دسترس نیست")
    NATIONAL_CODE_NOT_VALID = ("nationalCode.not_valid", "کد ملی نامعتبر است")
    INFO_IDENTITY_FOUND_NOT = ("info_identity.found_not", "اطلاعات هویتی یافت نشد")
    BANK_NOT_VALID = ("bank.not_valid", "شناسه بانک نامعتبر است")

    UNKNOWN_ERROR = ("JIBIT_500_UNKNOWN_ERROR", "خطای ناشناخته در سرویس جی‌بيت")

    def __new__(cls, code, message):
        obj = str.__new__(cls, code)
        obj._value_ = code
        obj._message_ = message
        return obj

    @property
    def code(self):
        return self.value

    @property
    def message(self):
        return self._message_

    def to_dict(self):
        return {"code": self.code, "message": self.message}

    @classmethod
    def from_code(cls, code: str):
        for member in cls:
            if member.code == code:
                return member
        return cls.UNKNOWN_ERROR

    def __str__(self):
        return self.code


class JibitException(Exception):
    def __init__(self, code: JibitErrorCode, detail: str = None, http_status: int = 500):
        self.code = code
        self.detail = detail or code.message
        self.http_status = http_status
        super().__init__(f"[{self.code.code}] {self.detail}")