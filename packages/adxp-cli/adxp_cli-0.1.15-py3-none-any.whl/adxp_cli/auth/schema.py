from pydantic import BaseModel, Field, field_validator
from typing import Optional


class AuthConfig(BaseModel):
    username: str
    client_id: str
    project_name: Optional[str] = None  # 선택적 필드로 변경
    base_url: str
    token: str
