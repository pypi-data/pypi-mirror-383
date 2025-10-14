from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Header(BaseModel):
    # core HTTP headers
    user_agent: str = Field(alias="User-Agent")
    referer: Optional[str] = Field(default=None, alias="Referer")
    accept: str = Field(alias="Accept")
    accept_language: str = Field(alias="Accept-Language")
    accept_encoding: str = Field(alias="Accept-Encoding")
    upgrade_insecure_requests: Optional[str] = Field(
        default=None, alias="Upgrade-Insecure-Requests"
    )
    connection: Optional[str] = Field(default=None, alias="Connection")

    # Fetch metadata headers
    sec_fetch_site: Optional[str] = Field(default=None, alias="Sec-Fetch-Site")
    sec_fetch_mode: Optional[str] = Field(default=None, alias="Sec-Fetch-Mode")
    sec_fetch_user: Optional[str] = Field(default=None, alias="Sec-Fetch-User")
    sec_fetch_dest: Optional[str] = Field(default=None, alias="Sec-Fetch-Dest")

    # Client hints
    sec_ch_ua: Optional[str] = Field(default=None, alias="Sec-CH-UA")
    sec_ch_ua_arch: Optional[str] = Field(default=None, alias="Sec-CH-UA-Arch")
    sec_ch_ua_bitness: Optional[str] = Field(default=None, alias="Sec-CH-UA-Bitness")
    sec_ch_ua_full_version_list: Optional[str] = Field(
        default=None, alias="Sec-CH-UA-Full-Version-List"
    )
    sec_ch_ua_mobile: Optional[str] = Field(default=None, alias="Sec-CH-UA-Mobile")
    sec_ch_ua_model: Optional[str] = Field(default=None, alias="Sec-CH-UA-Model")
    sec_ch_ua_platform: Optional[str] = Field(
        default=None, alias="Sec-CH-UA-Platform"
    )
    sec_ch_ua_platform_version: Optional[str] = Field(
        default=None, alias="Sec-CH-UA-Platform-Version"
    )

    model_config = {
        "populate_by_name": True,
        # 保持字段别名作为导出键
        "alias_generator": None
    }

    def to_ordered_list(self, order: List[str]) -> List[tuple[str, str]]:
        as_dict = self.model_dump(by_alias=True, exclude_none=True)
        ordered: List[tuple[str, str]] = []
        for key in order:
            if key in as_dict:
                ordered.append((key, as_dict[key]))
        # append any remaining keys in stable order
        for key in as_dict:
            if key not in order:
                ordered.append((key, as_dict[key]))
        return ordered

    def to_dict(self) -> Dict[str, str]:
        return self.model_dump(by_alias=True, exclude_none=True)


