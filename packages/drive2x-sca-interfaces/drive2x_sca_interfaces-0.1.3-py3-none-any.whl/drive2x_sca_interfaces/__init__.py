"""
SPDX-License-Identifier: LGPL-3.0-or-later
Copyright (C) 2025 Lappeenrannan-Lahden teknillinen yliopisto LUT
Author: Aleksei Romanenko <aleksei.romanenko@lut.fi>

Funded by the European Union and UKRI. Views and opinions expressed are however those of the author(s)
only and do not necessarily reflect those of the European Union, CINEA or UKRI. Neither the European
Union nor the granting authority can be held responsible for them.

Build EV status info example
>>> ev1 = ConnectedEVId(charge_point_id="some_id", evse_id=1)
>>> ev2 = ConnectedEVId(charge_point_id="another_id", evse_id=3)
>>> sca_data = SCADataEVs(values={ev1: SCADatum(soc=10.0, usable_battery_capacity_kwh=50, tdep=datetime.datetime(2025,10,1,tzinfo=datetime.timezone.utc)),\
                                  ev2: SCADatum(soc=30.0, usable_battery_capacity_kwh=20, tdep=datetime.datetime(2025,10,3,5,10,tzinfo=datetime.timezone.utc)),\
                                  },\
               soc_estimate_valid_at=datetime.datetime(2025,9,30,20,00,tzinfo=datetime.timezone.utc)).model_dump_json()
>>> sca_data
'{"values":{"some_id:1:1":{"soc":10.0,"usable_battery_capacity_kwh":50.0,"tdep":"2025-10-01T00:00:00Z"},"another_id:3:1":{"soc":30.0,"usable_battery_capacity_kwh":20.0,"tdep":"2025-10-03T05:10:00Z"}},"soc_estimate_valid_at":"2025-09-30T20:00:00Z"}'

Processed JSON input for EV status info
>>> parsed = SCADataEVs.model_validate(json.loads(sca_data))
>>> parsed  # doctest: +ELLIPSIS
SCADataEVs(values={ConnectedEVId(charge_point_id='some_id', evse_id=1, connector_id=1): SCADatum(soc=10.0, usable_battery_capacity_kwh=50.0, tdep=datetime.datetime(2025, 10, 1, 0, 0, tzinfo=TzInfo(...))), ConnectedEVId(charge_point_id='another_id', evse_id=3, connector_id=1): SCADatum(soc=30.0, usable_battery_capacity_kwh=20.0, tdep=datetime.datetime(2025, 10, 3, 5, 10, tzinfo=TzInfo(...)))}, soc_estimate_valid_at=datetime.datetime(2025, 9, 30, 20, 0, tzinfo=TzInfo(...)))
>>> parsed.model_dump_json()
'{"values":{"some_id:1:1":{"soc":10.0,"usable_battery_capacity_kwh":50.0,"tdep":"2025-10-01T00:00:00Z"},"another_id:3:1":{"soc":30.0,"usable_battery_capacity_kwh":20.0,"tdep":"2025-10-03T05:10:00Z"}},"soc_estimate_valid_at":"2025-09-30T20:00:00Z"}'

Build setpoint request
>>> request = SetpointRequestResponse(site_tag="some site",\
                                      expected_slot_start_time=datetime.datetime(2025,9,30,20,00,tzinfo=datetime.timezone.utc),\
                                      values={ev1: 100, ev2: -1000}).model_dump_json()
>>> request
'{"site_tag":"some site","expected_slot_start_time":"2025-09-30T20:00:00Z","values":{"some_id:1:1":100,"another_id:3:1":-1000}}'
>>> parsed_request = SetpointRequestResponse.model_validate(json.loads(request))
>>> parsed_request  # doctest: +ELLIPSIS
SetpointRequestResponse(site_tag='some site', expected_slot_start_time=datetime.datetime(2025, 9, 30, 20, 0, tzinfo=TzInfo(...)), values={ConnectedEVId(charge_point_id='some_id', evse_id=1, connector_id=1): 100, ConnectedEVId(charge_point_id='another_id', evse_id=3, connector_id=1): -1000})
>>> parsed_request.model_dump_json()
'{"site_tag":"some site","expected_slot_start_time":"2025-09-30T20:00:00Z","values":{"some_id:1:1":100,"another_id:3:1":-1000}}'
"""
import json

from pydantic import BaseModel, Field, field_validator
import datetime


def is_utc_time(x : datetime.datetime):
    return (x.tzinfo is not None) and (x.tzinfo.tzname(None) == "UTC")


class ConnectedEVId(BaseModel):
    """
    charge_point_id : str Unique identifier of a charge point. Can be a model-serial number pair or equivalent.
    evseid : int Unique number of charging equipment in terms of OCPP or equivalent
    connector_id : int Unique number of connector within the charging equipment in terms of OCPP or equivalent

    >>> ev_id = str(ConnectedEVId(charge_point_id="some_id", evse_id=2))
    >>> ev_id
    'some_id:2:1'
    >>> ConnectedEVId.from_string(ev_id)
    ConnectedEVId(charge_point_id='some_id', evse_id=2, connector_id=1)
    
    Supports colon in charge_point_id as follows
    >>> ev_id = str(ConnectedEVId(charge_point_id="some:id", evse_id=2))
    >>> ev_id
    'some:id:2:1'
    >>> ConnectedEVId.from_string(ev_id)
    ConnectedEVId(charge_point_id='some:id', evse_id=2, connector_id=1)
    """
    charge_point_id : str
    evse_id : int
    connector_id : int = 1

    @classmethod
    def from_string(cls, data : str):
        splits = data.split(":")
        charge_point_id = ":".join(splits[:-2])
        evse_id = int(splits[-2])
        connector_id = int(splits[-1])
        return ConnectedEVId(charge_point_id=charge_point_id,
                             evse_id=evse_id,
                             connector_id=connector_id)

    def __hash__(self) -> int:
        return str(self).__hash__()

    def __str__(self):
        return f"{self.charge_point_id}:{self.evse_id}:{self.connector_id}"

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

    @field_validator("values", mode='before')
    def decode_values(cls, x):
        validated = dict()
        for key, value in x.items():
            if isinstance(key, ConnectedEVId):
                validated[key] = value
            else:
                decoded_key = ConnectedEVId.from_string(key)
                validated[decoded_key] = value
        return validated
    
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


    @field_validator("values", mode='before')
    def decode_values(cls, x):
        validated = dict()
        for key, value in x.items():
            if isinstance(key, ConnectedEVId):
                validated[key] = value
            else:
                decoded_key = ConnectedEVId.from_string(key)
                validated[decoded_key] = value
        return validated

    @field_validator("soc_estimate_valid_at", mode='after')
    def soc_estimate_valid_at_is_utc(cls, x : datetime.datetime):
        if not is_utc_time(x):
            raise ValueError("soc_estimate_valid_at must be a timestamp in UTC")
        return x
