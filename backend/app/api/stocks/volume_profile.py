"""Estimate a fixed-range volume profile from one-minute candles."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from app.core.response import ApiResponse, success_response
from app.models.volume_profile import PriceLevel, VolumeProfileResult

from ._shared import MAX_TIMESTAMP, ProfileServiceDependency, Symbol


router = APIRouter()


class ProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: int = Field(ge=0, le=MAX_TIMESTAMP)
    end: int = Field(ge=0, le=MAX_TIMESTAMP)


class LevelResponse(BaseModel):
    priceCents: int
    lowPriceCents: int
    highPriceCents: int
    total: int
    buy: Literal[0] = 0
    sell: Literal[0] = 0
    neutral: Literal[0] = 0
    unknown: int
    delta: None = None
    node: Literal["HVN", "LVN"] | None


class ValueAreaResponse(BaseModel):
    low: int
    high: int
    volume: int


class DistributionResponse(BaseModel):
    levels: tuple[LevelResponse, ...]
    poc: LevelResponse
    total: int
    valueArea: ValueAreaResponse
    hasDirection: Literal[False] = False


class ProfileResponse(BaseModel):
    symbol: str
    start: int
    end: int
    actual_start: int
    actual_end: int
    calculation_method: Literal["estimated_1m_weighted_range"] = "estimated_1m_weighted_range"
    source: str
    data_source: str
    source_version: str
    data_version: str
    adjustment_version: str
    adjustment_source: str
    adjust: Literal["qfq"] = "qfq"
    volume_unit: Literal["shares"] = "shares"
    price_step: float
    total_volume: int
    price_levels: tuple[LevelResponse, ...]
    poc: float
    vah: float
    val: float
    profile: DistributionResponse
    complete: Literal[True] = True
    data_quality: dict[str, object]
    warnings: list[str]


def _level_response(level: PriceLevel) -> LevelResponse:
    return LevelResponse(
        priceCents=level.price_cents,
        lowPriceCents=level.low_price_cents,
        highPriceCents=level.high_price_cents,
        total=level.volume,
        unknown=level.volume,
        node=level.node,
    )


def _profile_response(symbol: str, result: VolumeProfileResult) -> ProfileResponse:
    distribution, quality = result.distribution, result.quality
    poc, area = distribution.poc, distribution.value_area
    actual_start, actual_end = quality["actual_start"], quality["actual_end"]
    assert poc is not None and area is not None and actual_start is not None and actual_end is not None
    levels = tuple(_level_response(level) for level in distribution.levels)
    warnings = ["按完整的 1 分钟 K 线估算，无法区分逐笔成交方向"]
    precision = quality["volume_precision_shares"]
    if precision is not None and precision > 1:
        warnings.append(f"该行情源按 {precision} 股粒度公布分钟成交量")
    return ProfileResponse(
        symbol=symbol,
        start=quality["requested_start"],
        end=quality["requested_end"],
        actual_start=actual_start,
        actual_end=actual_end,
        source=result.source,
        data_source=result.source,
        source_version=result.source_version,
        data_version=result.data_version,
        adjustment_version=result.adjustment_version,
        adjustment_source=result.adjustment_source,
        price_step=distribution.step_cents / 100,
        total_volume=distribution.total_volume,
        price_levels=levels,
        poc=poc.price_cents / 100,
        vah=area.high_cents / 100,
        val=area.low_cents / 100,
        profile=DistributionResponse(
            levels=levels,
            poc=_level_response(poc),
            total=distribution.total_volume,
            valueArea=ValueAreaResponse(low=area.low_cents, high=area.high_cents, volume=area.volume),
        ),
        data_quality=dict(quality),
        warnings=warnings,
    )


@router.post(
    "/{symbol}/volume-profile",
    response_model=ApiResponse[ProfileResponse],
    summary="基于 1 分钟 K 线估算价位分布",
)
def volume_profile(
    symbol: Symbol, body: ProfileRequest, service: ProfileServiceDependency,
) -> ApiResponse[ProfileResponse]:
    return success_response(_profile_response(symbol, service.calculate(symbol, body.start, body.end)))
