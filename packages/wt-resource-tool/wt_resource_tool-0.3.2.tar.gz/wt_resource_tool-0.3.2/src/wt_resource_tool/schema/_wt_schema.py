from typing import Literal

from pydantic import BaseModel, Field

type Country = Literal[
    "country_usa",
    "country_germany",
    "country_ussr",
    "country_britain",
    "country_japan",
    "country_france",
    "country_italy",
    "country_china",
    "country_sweden",
    "country_israel",
    "unknown",
]


class NameI18N(BaseModel):
    english: str
    french: str
    italian: str
    german: str
    spanish: str
    russian: str
    # polish: str
    # czech: str
    # turkish: str
    chinese: str
    japanese: str
    # portuguese: str
    # ukrainian: str
    # serbian: str
    # hungarian: str
    # korean: str
    # belarusian: str
    # romanian: str
    # vietnamese: str
    t_chinese: str
    h_chinese: str


class PlayerTitleDesc(BaseModel):
    title_id: str
    description_i18n: NameI18N | None = Field(default=None)
    name_i18n: NameI18N
    game_version: str


class ParsedPlayerTitleData(BaseModel):
    titles: list[PlayerTitleDesc]


class PlayerMedalDesc(BaseModel):
    medal_id: str
    country: Country
    name_i18n: NameI18N
    game_version: str

    def get_image_url(
        self,
        mode: Literal["normal", "big", "ribbon"] = "normal",
    ) -> str:
        prefix = (
            "https://cdn.jsdelivr.net/gh/gszabi99/War-Thunder-Datamine@refs/heads/master/atlases.vromfs.bin_u/medals"
        )
        if mode == "normal":
            return f"{prefix}/{self.medal_id}.png"
        elif mode == "big":
            return f"{prefix}/{self.medal_id}_big.png"
        elif mode == "ribbon":
            return f"{prefix}/{self.medal_id}_ribbon.png"


class ParsedPlayerMedalData(BaseModel):
    medals: list[PlayerMedalDesc]


class VehicleDesc(BaseModel):
    vehicle_id: str
    name_shop_i18n: NameI18N | None
    name_0_i18n: NameI18N | None
    name_1_i18n: NameI18N | None
    name_2_i18n: NameI18N | None
    rank: int
    economic_rank_arcade: int
    economic_rank_historical: int
    economic_rank_simulation: int

    economic_rank_tank_historical: int | None = Field(default=None)
    economic_rank_tank_simulation: int | None = Field(default=None)

    country: Country
    unit_class: str
    spawn_type: str | None = Field(
        default=None,
    )
    value: int
    req_exp: int | None = Field(
        default=None,
    )
    train_cost: int
    train2_cost: int
    train3_cost_gold: int
    train3_cost_exp: int
    repair_cost_arcade: int
    repair_cost_historical: int
    repair_cost_simulation: int
    repair_cost_per_min_arcade: int
    repair_cost_per_min_historical: int
    repair_cost_per_min_simulation: int
    repair_cost_full_upgraded_arcade: int | None = Field(
        default=None,
    )
    repair_cost_full_upgraded_historical: int | None = Field(
        default=None,
    )
    repair_cost_full_upgraded_simulation: int | None = Field(
        default=None,
    )
    reward_mul_arcade: float = Field(
        default=0,
    )
    reward_mul_historical: float
    reward_mul_simulation: float
    exp_mul: float
    req_air: str | None = Field(
        default=None,
    )
    reload_time_cannon: float | None = Field(
        default=None,
    )
    crew_total_count: int | None = Field(default=None)

    primary_weapon_auto_loader: bool | None = Field(default=None)

    cost_gold: int | None = Field(default=None)

    turret_speed: list[float] | None = Field(default=None)

    gift: str | None = Field(default=None)

    research_type: str | None = Field(default=None)

    game_version: str

    def get_icon_url(
        self,
    ) -> str:
        return f"https://cdn.jsdelivr.net/gh/gszabi99/War-Thunder-Datamine@refs/heads/master/atlases.vromfs.bin_u/units/{self.vehicle_id}.png"


class ParsedVehicleData(BaseModel):
    vehicles: list[VehicleDesc]
