"""
SPDX-License-Identifier: LGPL-3.0-or-later
Copyright (C) 2025 Lappeenrannan-Lahden teknillinen yliopisto LUT
Author: Aleksei Romanenko <aleksei.romanenko@lut.fi>

Funded by the European Union and UKRI. Views and opinions expressed are however those of the author(s)
only and do not necessarily reflect those of the European Union, CINEA or UKRI. Neither the European
Union nor the granting authority can be held responsible for them.
"""

from pydantic import BaseModel, Field, field_validator
import datetime


def is_utc_time(x : datetime.datetime):
    return (x.tzinfo is not None) and (x.tzinfo.tzname(None) == "UTC")


class ConnectedEVId(BaseModel):
    """
    charge_point_id : str Unique identifier of a charge point. Can be a model-serial number pair or equivalent.
    evseid : int Unique number of charging equipment in terms of OCPP or equivalent
    connector_id : int Unique number of connector within the charging equipment in terms of OCPP or equivalent
    """
    charge_point_id : str
    evse_id : int
    connector_id : int = 1

    def __hash__(self) -> int:
        return f"{self.charge_point_id}:{self.evse_id}:{self.connector_id}".__hash__()

class SetpointRequestResponse(BaseModel):
    """
    When used as request means the command that should be implemented by the chargers.
    When used as response means the actual values confirmed for implementation by the CSMS or equivalent system.

    site_tag : str Unique identifier of a demo site. Used to map specific charge points to a Smart Charging Algorithm run
    values : dict[ConnectedEVId, int] Maps the next commanded setpoint in Watts to EVs by their ConnectedEVId
    expected_slot_start_time : datetime.datetime in UTC describing the first moment in time when the commanded reference
                               should be applied to Charge Controller setpoints.
    """
    site_tag : str
    expected_slot_start_time : datetime.datetime
    values : dict[ConnectedEVId, int] = Field(default_factory=dict)

    @field_validator("expected_slot_start_time", mode='after')
    def expected_slot_start_time_is_utc(cls, x : datetime.datetime):
        if not is_utc_time(x):
            raise ValueError("expected_slot_start_time must be a timestamp in UTC")
        return x

class SCADatum(BaseModel):
    """

    soc : float Percentage value in range (0.0-100.0 %) in relation to usable_battery_capacity_kwh
    usable_battery_capacity_kwh : float Total USABLE battery capacity of EV. If the car has HW safety margins these
                                        should be excluded
    tdep : datetime.datetime The forecasted or declared departure time of the connected EV in UTC.

    """
    soc : float
    usable_battery_capacity_kwh : float
    tdep : datetime.datetime

    @field_validator("usable_battery_capacity_kwh", mode='after')
    def usable_battery_capacity_kwh_is_positive(cls, x : float):
        if not x > 0.0:
            raise ValueError("usable_battery_capacity_kwh must be a positive number")
        return x

    @field_validator("soc", mode='after')
    def soc_in_range(cls, x : float):
        if not 0.0 <= x <= 100.0:
            raise ValueError("soc must be a value in percents of total usable capacity in range 0..100 %")
        return x

    @field_validator("tdep", mode='after')
    def tdep_is_utc(cls, x : datetime.datetime):
        if not is_utc_time(x):
            raise ValueError("tdep must be a timestamp in UTC")
        return x

class SCADataEVs(BaseModel):
    """

    This is the informative structure that provides SCA with the estimated values of SoC for all EVs available for the
    SCA scheduling.

    values : dict[ConnectedEVId, int] Maps the SCADatum information about EV for each EV by their ConnectedEVId
    soc_estimate_valid_at : datetime.datetime UTC timestamp for which the SoC values are estimated. E.g. if data is
            reported "as is" it should be equal to the moment of response generation. Otherwise, the respondent is expected
            to provide some for of estimation for the reported time based on the latest available dat aat the moment of polling
            and the current trend for that value.
    """
    values : dict[ConnectedEVId, SCADatum] = Field(default_factory=dict)
    soc_estimate_valid_at :datetime.datetime


    @field_validator("soc_estimate_valid_at", mode='after')
    def soc_estimate_valid_at_is_utc(cls, x : datetime.datetime):
        if not is_utc_time(x):
            raise ValueError("soc_estimate_valid_at must be a timestamp in UTC")
        return x
