import re
from datetime import datetime, date

class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message):
        super().__init__(message)

def emailvalidate(email):
    """Check if the email ends with @gmail.com or @hotmail.com."""
    if "@gmail.com" in email or "@hotmail.com" in email:
        return True
    raise ValidationError("Email @gmail.com yoki @hotmail.com bilan tugashi shart!")

def pass8and64(password):
    """Check if password length is between 8 and 64 characters."""
    if len(password) < 8:
        raise ValidationError("Few symbols in password")
    elif len(password) > 64:
        raise ValidationError("Too many symbols in password")
    return True

def username_validator(username: str) -> bool:
    """Tekshiradi: faqat harf va raqamlardan iborat, uzunligi 3–20."""
    if not isinstance(username, str):
        raise ValidationError("Username matn (str) bo‘lishi kerak.")
    if not username.isalnum():
        raise ValidationError("Username faqat harflar va raqamlardan iborat bo‘lishi kerak.")
    if not (3 <= len(username) <= 20):
        raise ValidationError("Username uzunligi 3 dan 20 tagacha bo‘lishi kerak.")
    return True

def fullname_validator(fullname: str) -> bool:
    """Tekshiradi: kamida 2 ta so‘z, faqat harf va bo‘sh joylardan iborat."""
    if not isinstance(fullname, str):
        raise ValidationError("Fullname matn (str) bo‘lishi kerak.")
    if len(fullname.strip().split()) < 2:
        raise ValidationError("To‘liq ism-sharif kiriting (kamida 2 ta so‘z).")
    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ'\s\-]+$", fullname):
        raise ValidationError("Ismda faqat harflar, bo‘sh joy va tire bo‘lishi mumkin.")
    return True

def phone_validator(phone: str) -> bool:
    """Tekshiradi: telefon raqami formati to‘g‘rimi (+998901234567 yoki 901234567)."""
    if not isinstance(phone, str):
        raise ValidationError("Telefon raqami matn (str) bo‘lishi kerak.")
    if not re.match(r"^(\+?998)?[0-9]{9}$", phone):
        raise ValidationError("Telefon raqami noto‘g‘ri formatda. Masalan: +998901234567 yoki 901234567.")
    return True

def birthdate_validator(birthdate: str) -> bool:
    """Tekshiradi: tug‘ilgan sana to‘g‘rimi (YYYY-MM-DD) va foydalanuvchi yoshi 13 dan katta."""
    if not isinstance(birthdate, str):
        raise ValidationError("Sana matn (str) bo‘lishi kerak.")
    try:
        bdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Sana formati noto‘g‘ri. To‘g‘ri format: YYYY-MM-DD")

    today = date.today()
    age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))

    if bdate > today:
        raise ValidationError("Tug‘ilgan sana kelajakda bo‘lishi mumkin emas.")
    if age < 13:
        raise ValidationError("Foydalanuvchi yoshi kamida 13 yosh bo‘lishi kerak.")
    return True
