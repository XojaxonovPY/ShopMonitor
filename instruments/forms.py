from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator


class LoginForm(BaseModel):
    email: EmailStr = None
    password: str = None


class RegisterForm(BaseModel):
    full_name: str = None
    email: EmailStr = None
    password: str = Field(min_length=4)


class VerifyCodeForm(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UrlForm(BaseModel):
    url: HttpUrl

    @field_validator("url")
    def check_domain(cls, v: HttpUrl):
        allowed_domains = ['clickbrandshop.robostore.uz', 'uzum.uz']
        if not any(domain in v.host for domain in allowed_domains):
            raise ValueError("Faqat clickbrandshop,uzummarket linklariga ruxsat beriladi")
        return v
