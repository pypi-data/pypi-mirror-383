from enum import Enum


class JibitErrorCode(Enum):
    FORBIDDEN = ("forbidden", "دسترسی غیرمجاز")
    INVALID_REQUEST_BODY = ("invalid.request_body", "بدنه درخواست نامعتبر است")
    BALANCE_NOT_ENOUGH = ("balance.not_enough", "موجودی کافی نیست")
    PROVIDERS_NOT_AVAILABLE = ("providers.not_available", "سرویس‌دهنده در دسترس نیست")

    INFO_IDENTITY_FOUND_NOT = ("info_identity.found_not", "اطلاعات هویتی یافت نشد")

    IBAN_IS_REQUIRED = ("iban.required_is", "شبا است")
    IBAN_NOT_VALID  = ("iban.valid_not", "شبا معتبر است")

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

    BIRTHDATE_NOT_VALID = ("birthDate.not_valid", "تاریخ تولد معتبر نیست")

    DAILY_LIMIT_REACHED = ("daily_limit.reached", "سقف روزانه تراکنش‌ها پر شده است")
    PARAMETERS_NOT_ACCEPTABLE = ("parameters.not_acceptable", "پارامترهای ارسالی نامعتبر هستند")

    INVALID_CARD = ("JIBIT_400_INVALID_CARD", "کارت نامعتبر است")
    UNAUTHORIZED = ("JIBIT_401_UNAUTHORIZED", "توکن معتبر نیست یا منقضی شده است")
    SERVICE_UNAVAILABLE = ("JIBIT_503_UNAVAILABLE", "سرویس جی‌بيت در دسترس نیست")
    UNKNOWN_ERROR = ("JIBIT_500_UNKNOWN_ERROR", "خطای ناشناخته در سرویس جی‌بيت")

    @property
    def code(self) -> str:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]

    @classmethod
    def from_code(cls, code: str) -> "JibitErrorCode":
        for member in cls:
            if member.code == code:
                return member
        return cls.UNKNOWN_ERROR

    def __str__(self) -> str:
        return self.code


class JibitException(Exception):
    def __init__(self, code: JibitErrorCode, detail: str = None, http_status: int = 500):
        self.code = code
        self.detail = detail or code.message
        self.http_status = http_status
        super().__init__(f"[{self.code.code}] {self.detail}")