"""
SPDX-License-Identifier: LGPL-3.0-or-later
Copyright (C) 2025 Lappeenrannan-Lahden teknillinen yliopisto LUT
Author: Aleksei Romanenko <aleksei.romanenko@lut.fi>

Funded by the European Union and UKRI. Views and opinions expressed are however those of the author(s)
only and do not necessarily reflect those of the European Union, CINEA or UKRI. Neither the European
Union nor the granting authority can be held responsible for them.
"""
from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator
import datetime



class ConnectedEVId(BaseModel):
    """
    charge_point_id : str Unique identifier of a charge point. Can be a model-serial number pair or equivalent.
    evseid : int Unique number of charging equipment in terms of OCPP or equivalent
    connector_id : int Unique number of connector within the charging equipment in terms of OCPP or equivalent
    """
    charge_point_id : str
    evse_id : int
    connector_id : int = 1

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
    expected_slot_start_time : Annotated[datetime.datetime, AfterValidator(lambda x: x.tzinfo.tzname() == "UTC")]
    values : dict[ConnectedEVId, int] = Field(default_factory=dict)


class SCADatum(BaseModel):
    """

    soc : float Percentage value in range (0.0-100.0 %) in relation to usable_battery_capacity_kwh
    usable_battery_capacity_kwh : float Total USABLE battery capacity of EV. If the car has HW safety margins these
                                        should be excluded
    tdep : datetime.datetime The forecasted or declared departure time of the connected EV in UTC.

    """
    soc : Annotated[float, AfterValidator(lambda x: 0.0 <= x <= 100.0)]
    usable_battery_capacity_kwh : Annotated[float, AfterValidator(lambda x: x > 0.0)]
    tdep : Annotated[datetime.datetime, AfterValidator(lambda x: x.tzinfo.tzname() == "UTC")]

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
    soc_estimate_valid_at : Annotated[datetime.datetime, AfterValidator(lambda x: x.tzinfo.tzname() == "UTC")]

