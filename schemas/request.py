from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class RegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=4, max_length=15)


class UrlSchema(BaseModel):
    url: HttpUrl

    @field_validator("url")
    def check_domain(cls, v: HttpUrl):
        allowed_domains = ['clickbrandshop.robostore.uz', 'uzum.uz']
        if not any(domain in v.host for domain in allowed_domains):
            raise ValueError("Faqat clickbrandshop,uzummarket linklariga ruxsat beriladi")
        return v
