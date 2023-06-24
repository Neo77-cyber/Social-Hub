from passlib.context import CryptContext




SECRET_KEY = "FMe1o0baNLQ_ntPVuK2FTGWwxc_m1KfuKWp0xgReaJg"

ACCESS_TOKEN_EXPIRE_MINUTES = 1440

password_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")  