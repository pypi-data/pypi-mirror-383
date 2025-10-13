import datetime
import enum
import time
import queue
import inspect
import logging

from typing import TypedDict, Any, Self

from .momonga_exception import (MomongaResponseNotExpected,
                                MomongaResponseNotPossible,
                                MomongaNeedToReopen,
                                MomongaRuntimeError)
from .momonga_response import SkEventRxUdp
from .momonga_session_manager import MomongaSessionManager
from .momonga_session_manager import logger as session_manager_logger
from .momonga_sk_wrapper import logger as sk_wrapper_logger

logger = logging.getLogger(__name__)


class EchonetServiceCode(enum.IntEnum):
    set_c: int = 0x61
    get: int = 0x62


class EchonetPropertyCode(enum.IntEnum):
    operation_status: int = 0x80
    installation_location: int = 0x81
    standard_version_information: int = 0x82
    fault_status: int = 0x88
    manufacturer_code: int = 0x8A
    serial_number: int = 0x8D
    current_time_setting: int = 0x97
    current_date_setting: int = 0x98
    properties_for_status_notification: int = 0x9D
    properties_to_set_values: int = 0x9E
    properties_to_get_values: int = 0x9F
    route_b_id: int = 0xC0
    one_minute_measured_cumulative_energy: int = 0xD0
    coefficient_for_cumulative_energy: int = 0xD3
    number_of_effective_digits_for_cumulative_energy: int = 0xD7
    measured_cumulative_energy: int = 0xE0
    measured_cumulative_energy_reversed: int = 0xE3
    unit_for_cumulative_energy: int = 0xE1
    historical_cumulative_energy_1: int = 0xE2
    historical_cumulative_energy_1_reversed: int = 0xE4
    day_for_historical_data_1: int = 0xE5
    instantaneous_power: int = 0xE7
    instantaneous_current: int = 0xE8
    cumulative_energy_measured_at_fixed_time: int = 0xEA
    cumulative_energy_measured_at_fixed_time_reversed: int = 0xEB
    historical_cumulative_energy_2: int = 0xEC
    time_for_historical_data_2: int = 0xED
    historical_cumulative_energy_3: int = 0xEE
    time_for_historical_data_3: int = 0xEF


class EchonetProperty:
    def __init__(self,
                 epc: EchonetPropertyCode | int,
                 ) -> None:
        self.epc = epc


class EchonetPropertyWithData:
    def __init__(self,
                 epc: EchonetPropertyCode | int,
                 edt: bytes | None = None,
                 ) -> None:
        self.epc = epc
        self.edt = edt


class EchonetDataParser:
    @classmethod
    def parse_operation_status(cls, edt: bytes) -> bool | None:
        status = int.from_bytes(edt, 'big')
        if status == 0x30:  # turned on
            status = True
        elif status == 0x31:  # turned off
            status = False
        else:
            status = None  # unknown

        return status

    @classmethod
    def parse_installation_location(cls, edt: bytes) -> str:
        code = edt[0]
        if code == 0x00:
            location = 'location not set'
        elif code == 0x01:
            location = 'location information: ' + edt[1:].hex()
        elif 0x02 <= code <= 0x07:  # reserved for future use
            location = 'not implemented'
        elif 0x08 <= code <= 0x7F:
            location_map = {
                1: 'living room',
                2: 'dining room',
                3: 'kitchen',
                4: 'bathroom',
                5: 'toilet',
                6: 'washroom',
                7: 'hallway',
                8: 'room',
                9: 'stairs',
                10: 'entrance',
                11: 'storage room',
                12: 'garden/perimeter',
                13: 'garage',
                14: 'veranda',
                15: 'other',
            }
            location_code = code >> 3
            location = location_map[location_code]
            location += ' ' + str(code & 0x07)
        elif 0x80 <= code <= 0xFE:  # reserved for future use
            location = 'not implemented'
        elif code == 0xFF:
            location = 'location not fixed'
        else:
            location = 'unknown'

        return location

    @classmethod
    def parse_standard_version_information(cls, edt: bytes) -> str:
        version = ''
        if edt[0] > 0:
            version += chr(edt[0])
        if edt[1] > 0:
            version += chr(edt[1])
        return version + chr(edt[2]) + '.' + str(edt[3])

    @classmethod
    def parse_fault_status(cls, edt: bytes) -> bool:
        status_code = int.from_bytes(edt, 'big')
        if status_code == 0x41:
            status = True  # fault occurred
        elif status_code == 0x42:
            status = False  # no fault occurred
        else:
            status = None  # unknown

        return status

    @classmethod
    def parse_manufacturer_code(cls, edt: bytes) -> bytes:
        return edt

    @classmethod
    def parse_serial_number(cls, edt: bytes) -> str:
        return edt.decode()

    @classmethod
    def parse_current_time_setting(cls, edt: bytes) -> datetime.time:
        hour = edt[0]
        minute = edt[1]
        return datetime.time(hour=hour, minute=minute, second=0)

    @classmethod
    def parse_current_date_setting(cls, edt: bytes) -> datetime.date:
        year = int.from_bytes(edt[0:2], 'big')
        month = edt[2]
        day = edt[3]
        return datetime.date(year=year, month=month, day=day)

    @classmethod
    def parse_property_map(cls, edt: bytes) -> set[EchonetPropertyCode | int]:
        num_of_properties = edt[0]
        property_map = edt[1:]
        properties = set()
        if num_of_properties < 16:
            for prop_code in property_map:
                try:
                    prop_code = EchonetPropertyCode(prop_code)
                except ValueError:
                    pass

                properties.add(prop_code)
        else:
            for i in range(len(property_map)):
                b = property_map[i]
                for j in range(8):
                    if b & 1 << j:
                        prop_code = (j + 0x08 << 4) + i
                        try:
                            prop_code = EchonetPropertyCode(prop_code)
                        except ValueError:
                            pass

                        properties.add(prop_code)

        return properties

    @classmethod
    def parse_route_b_id(cls, edt: bytes) -> dict[str, bytes]:
        manufacturer_code = edt[1:4]
        authentication_id = edt[4:]
        return {'manufacturer code': manufacturer_code, 'authentication id': authentication_id}

    @classmethod
    def parse_one_minute_measured_cumulative_energy(
            cls,
            edt: bytes,
            energy_unit: int | float,
            energy_coefficient: int,
    ) -> dict[str, datetime.datetime | dict[str, int | float | None]]:
        timestamp = datetime.datetime(int.from_bytes(edt[0:2], 'big'),
                                      edt[2], edt[3], edt[4], edt[5], edt[6])

        normal_direction_energy = int.from_bytes(edt[7:11], 'big')
        if normal_direction_energy == 0xFFFFFFFE:
            normal_direction_energy = None
        else:
            normal_direction_energy *= energy_unit
            normal_direction_energy *= energy_coefficient

        reverse_direction_energy = int.from_bytes(edt[11:15], 'big')
        if reverse_direction_energy == 0xFFFFFFFE:
            reverse_direction_energy = None
        else:
            reverse_direction_energy *= energy_unit
            reverse_direction_energy *= energy_coefficient

        return {'timestamp': timestamp,
                'cumulative energy': {'normal direction': normal_direction_energy,
                                      'reverse direction': reverse_direction_energy}}

    @classmethod
    def parse_coefficient_for_cumulative_energy(cls, edt: bytes) -> int:
        coefficient = int.from_bytes(edt, 'big')
        return coefficient

    @classmethod
    def parse_number_of_effective_digits_for_cumulative_energy(cls, edt: bytes) -> int:
        digits = int.from_bytes(edt, 'big')
        return digits

    @classmethod
    def parse_measured_cumulative_energy(
            cls,
            edt: bytes,
            energy_unit: int | float,
            energy_coefficient: int,
    ) -> int | float:
        cumulative_energy = int.from_bytes(edt, 'big')
        cumulative_energy *= energy_unit
        cumulative_energy *= energy_coefficient
        return cumulative_energy

    @classmethod
    def parse_unit_for_cumulative_energy(cls, edt: bytes) -> int | float:
        unit_index = int.from_bytes(edt, 'big')
        unit_map = {0x00: 1,
                    0x01: 0.1,
                    0x02: 0.01,
                    0x03: 0.001,
                    0x04: 0.0001,
                    0x0A: 10,
                    0x0B: 100,
                    0x0C: 1000,
                    0x0D: 10000}
        unit = unit_map.get(unit_index)
        if unit is None:
            raise MomongaRuntimeError('Obtained unit for cumulative energy (%X) is not defined.' % unit_index)

        return unit

    @classmethod
    def parse_historical_cumulative_energy_1(
            cls,
            edt: bytes,
            energy_unit: int | float,
            energy_coefficient: int,
    ) -> list[dict[str, datetime.datetime | int | float | None]]:
        day = int.from_bytes(edt[0:2], 'big')
        timestamp = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
        timestamp -= datetime.timedelta(days=day)
        energy_data_points = edt[2:]
        historical_cumulative_energy = []
        for i in range(48):
            j = i * 4
            cumulative_energy = int.from_bytes(energy_data_points[j:j + 4], 'big')
            if cumulative_energy == 0xFFFFFFFE:
                cumulative_energy = None
            else:
                cumulative_energy *= energy_unit
                cumulative_energy *= energy_coefficient
            historical_cumulative_energy.append({'timestamp': timestamp, 'cumulative energy': cumulative_energy})
            timestamp += datetime.timedelta(minutes=30)

        return historical_cumulative_energy

    @classmethod
    def parse_day_for_historical_data_1(cls, edt: bytes) -> int:
        day = int.from_bytes(edt, 'big')
        return day

    @classmethod
    def parse_instantaneous_power(cls, edt: bytes) -> float:
        power = int.from_bytes(edt, 'big', signed=True)
        return power

    @classmethod
    def parse_instantaneous_current(cls, edt: bytes) -> dict[str, float]:
        r_phase_current = int.from_bytes(edt[0:2], 'big', signed=True)
        t_phase_current = int.from_bytes(edt[2:4], 'big', signed=True)
        r_phase_current *= 0.1  # to Ampere
        t_phase_current *= 0.1  # to Ampere
        return {'r phase current': r_phase_current, 't phase current': t_phase_current}

    @classmethod
    def parse_cumulative_energy_measured_at_fixed_time(
            cls,
            edt: bytes,
            energy_unit: int | float,
            energy_coefficient: int,
    ) -> dict[str, datetime.datetime | int | float]:
        timestamp = datetime.datetime(int.from_bytes(edt[0:2], 'big'),
                                      edt[2], edt[3], edt[4], edt[5], edt[6])
        cumulative_energy = int.from_bytes(edt[7:], 'big')
        cumulative_energy *= energy_unit
        cumulative_energy *= energy_coefficient
        return {'timestamp': timestamp, 'cumulative energy': cumulative_energy}

    @classmethod
    def parse_historical_cumulative_energy_2(
            cls,
            edt: bytes,
            energy_unit: int | float,
            energy_coefficient: int,
    ) -> list[dict[str, datetime.datetime |
                         dict[str, int | float | None]]]:
        year = int.from_bytes(edt[0:2], 'big')
        num_of_data_points = edt[6]
        energy_data_points = edt[7:]
        timestamp = datetime.datetime(year, edt[2], edt[3], edt[4], edt[5])
        historical_cumulative_energy = []
        for i in range(num_of_data_points):
            j = i * 8
            normal_direction_energy = int.from_bytes(energy_data_points[j:j + 4], 'big')
            if normal_direction_energy == 0xFFFFFFFE:
                normal_direction_energy = None
            else:
                normal_direction_energy *= energy_unit
                normal_direction_energy *= energy_coefficient

            reverse_direction_energy = int.from_bytes(energy_data_points[j + 4:j + 8], 'big')
            if reverse_direction_energy == 0xFFFFFFFE:
                reverse_direction_energy = None
            else:
                reverse_direction_energy *= energy_unit
                reverse_direction_energy *= energy_coefficient

            historical_cumulative_energy.append(
                {'timestamp': timestamp,
                 'cumulative energy': {'normal direction': normal_direction_energy,
                                       'reverse direction': reverse_direction_energy}})
            timestamp -= datetime.timedelta(minutes=30)

        return historical_cumulative_energy

    @classmethod
    def parse_time_for_historical_data_2(cls, edt: bytes) -> dict[str, datetime.datetime | None | int]:
        year = int.from_bytes(edt[0:2], 'big')
        if year == 0xFFFF:
            timestamp = None
        else:
            timestamp = datetime.datetime(year, edt[2], edt[3], edt[4], edt[5])

        num_of_data_points = edt[6]
        return {'timestamp': timestamp,
                'number of data points': num_of_data_points}

    @classmethod
    def parse_historical_cumulative_energy_3(
            cls,
            edt: bytes,
            energy_unit: int | float,
            energy_coefficient: int,
    ) -> list[dict[str, datetime.datetime |
                        dict[str, dict[str, int | float | None]]]]:
        year = int.from_bytes(edt[0:2], 'big')
        num_of_data_points = edt[6]
        energy_data_points = edt[7:]
        timestamp = datetime.datetime(year, edt[2], edt[3], edt[4], edt[5])
        historical_cumulative_energy = []
        for i in range(num_of_data_points):
            j = i * 8
            normal_direction_energy = int.from_bytes(energy_data_points[j:j + 4], 'big')
            if normal_direction_energy == 0xFFFFFFFE:
                normal_direction_energy = None
            else:
                normal_direction_energy *= energy_unit
                normal_direction_energy *= energy_coefficient

            reverse_direction_energy = int.from_bytes(energy_data_points[j + 4:j + 8], 'big')
            if reverse_direction_energy == 0xFFFFFFFE:
                reverse_direction_energy = None
            else:
                reverse_direction_energy *= energy_unit
                reverse_direction_energy *= energy_coefficient

            historical_cumulative_energy.append(
                {'timestamp': timestamp,
                 'cumulative energy': {'normal direction': normal_direction_energy,
                                       'reverse direction': reverse_direction_energy}})
            timestamp -= datetime.timedelta(minutes=1)

        return historical_cumulative_energy

    @classmethod
    def parse_time_for_historical_data_3(cls, edt: bytes) -> dict[str, datetime.datetime | None | int]:
        year = int.from_bytes(edt[0:2], 'big')
        if year == 0xFFFF:
            timestamp = None
        else:
            timestamp = datetime.datetime(year, edt[2], edt[3], edt[4], edt[5])

        num_of_data_points = edt[6]
        return {'timestamp': timestamp,
                'number of data points': num_of_data_points}


parser_map: dict[EchonetPropertyCode, callable] = {
    EchonetPropertyCode.operation_status: EchonetDataParser.parse_operation_status,
    EchonetPropertyCode.installation_location: EchonetDataParser.parse_installation_location,
    EchonetPropertyCode.standard_version_information: EchonetDataParser.parse_standard_version_information,
    EchonetPropertyCode.fault_status: EchonetDataParser.parse_fault_status,
    EchonetPropertyCode.manufacturer_code: EchonetDataParser.parse_manufacturer_code,
    EchonetPropertyCode.serial_number: EchonetDataParser.parse_serial_number,
    EchonetPropertyCode.current_time_setting: EchonetDataParser.parse_current_time_setting,
    EchonetPropertyCode.current_date_setting: EchonetDataParser.parse_current_date_setting,
    EchonetPropertyCode.properties_for_status_notification: EchonetDataParser.parse_property_map,
    EchonetPropertyCode.properties_to_set_values: EchonetDataParser.parse_property_map,
    EchonetPropertyCode.properties_to_get_values: EchonetDataParser.parse_property_map,
    EchonetPropertyCode.route_b_id: EchonetDataParser.parse_route_b_id,
    EchonetPropertyCode.one_minute_measured_cumulative_energy: EchonetDataParser.parse_one_minute_measured_cumulative_energy,
    EchonetPropertyCode.coefficient_for_cumulative_energy: EchonetDataParser.parse_coefficient_for_cumulative_energy,
    EchonetPropertyCode.number_of_effective_digits_for_cumulative_energy: EchonetDataParser.parse_number_of_effective_digits_for_cumulative_energy,
    EchonetPropertyCode.measured_cumulative_energy: EchonetDataParser.parse_measured_cumulative_energy,
    EchonetPropertyCode.measured_cumulative_energy_reversed: EchonetDataParser.parse_measured_cumulative_energy,
    EchonetPropertyCode.unit_for_cumulative_energy: EchonetDataParser.parse_unit_for_cumulative_energy,
    EchonetPropertyCode.historical_cumulative_energy_1: EchonetDataParser.parse_historical_cumulative_energy_1,
    EchonetPropertyCode.historical_cumulative_energy_1_reversed: EchonetDataParser.parse_historical_cumulative_energy_1,
    EchonetPropertyCode.day_for_historical_data_1: EchonetDataParser.parse_day_for_historical_data_1,
    EchonetPropertyCode.instantaneous_power: EchonetDataParser.parse_instantaneous_power,
    EchonetPropertyCode.instantaneous_current: EchonetDataParser.parse_instantaneous_current,
    EchonetPropertyCode.cumulative_energy_measured_at_fixed_time: EchonetDataParser.parse_cumulative_energy_measured_at_fixed_time,
    EchonetPropertyCode.cumulative_energy_measured_at_fixed_time_reversed: EchonetDataParser.parse_cumulative_energy_measured_at_fixed_time,
    EchonetPropertyCode.historical_cumulative_energy_2: EchonetDataParser.parse_historical_cumulative_energy_2,
    EchonetPropertyCode.time_for_historical_data_2: EchonetDataParser.parse_time_for_historical_data_2,
    EchonetPropertyCode.historical_cumulative_energy_3: EchonetDataParser.parse_historical_cumulative_energy_3,
    EchonetPropertyCode.time_for_historical_data_3: EchonetDataParser.parse_time_for_historical_data_3,
}


class EchonetDataBuilder:
    @classmethod
    def build_edata_to_set_day_for_historical_data_1(cls, day: int = 0) -> bytes:
        if day < 0 or day > 99:
            raise ValueError('The parameter "day" must be between 0 and 99.')

        return day.to_bytes(1, 'big')

    @classmethod
    def build_edata_to_set_time_for_historical_data_2(cls,
                                                      timestamp: datetime.datetime,
                                                      num_of_data_points: int = 12,
                                                      ) -> bytes:
        if num_of_data_points < 1 or num_of_data_points > 12:
            raise ValueError('The parameter "num_of_data_points" must be between 1 and 12.')

        if timestamp.year < 1 or timestamp.year > 9999:
            raise ValueError('The year specified by the parameter "timestamp" must be between 1 and 9999.')

        year = timestamp.year.to_bytes(2, 'big')
        month = timestamp.month.to_bytes(1, 'big')
        day = timestamp.day.to_bytes(1, 'big')
        hour = timestamp.hour.to_bytes(1, 'big')
        if 0 <= timestamp.minute < 30:
            minute = 0
        else:
            minute = 30

        minute = minute.to_bytes(1, 'big')
        num_of_data_points = num_of_data_points.to_bytes(1, 'big')
        return year + month + day + hour + minute + num_of_data_points

    @classmethod
    def build_edata_to_set_time_for_historical_data_3(cls,
                                                      timestamp: datetime.datetime,
                                                      num_of_data_points: int = 10,
                                                      ) -> bytes:
        if num_of_data_points < 1 or num_of_data_points > 10:
            raise ValueError('The parameter "num_of_data_points" must be between 1 and 10.')

        if timestamp.year < 1 or timestamp.year > 9999:
            raise ValueError('The year specified by the parameter "timestamp" must be between 1 and 9999.')

        year = timestamp.year.to_bytes(2, 'big')
        month = timestamp.month.to_bytes(1, 'big')
        day = timestamp.day.to_bytes(1, 'big')
        hour = timestamp.hour.to_bytes(1, 'big')
        minute = timestamp.minute.to_bytes(1, 'big')
        num_of_data_points = num_of_data_points.to_bytes(1, 'big')
        return year + month + day + hour + minute + num_of_data_points


class Momonga:
    def __init__(self,
                 rbid: str,
                 pwd: str,
                 dev: str,
                 baudrate: int = 115200,
                 reset_dev: bool = True,
                 ) -> None:
        self.xmit_retries: int = 12
        self.recv_timeout: int | float = 12
        self.internal_xmit_interval: int | float = 5
        self.transaction_id: int = 0
        self.energy_unit: int | float = 1
        self.energy_coefficient: int = 1
        self.is_open: bool = False
        self.session_manager = MomongaSessionManager(rbid, pwd, dev, baudrate, reset_dev)

    def __init_energy_unit(self) -> None:
        logger.debug('Initializing the energy unit and coefficient.')
        self.energy_unit = self.get_unit_for_cumulative_energy()
        try:
            self.energy_coefficient = self.get_coefficient_for_cumulative_energy()
            time.sleep(self.internal_xmit_interval)
        except MomongaResponseNotPossible:  # due to the property 0xD3 is optional.
            self.energy_coefficient = 1
        time.sleep(self.internal_xmit_interval)

    def __enter__(self) -> Self:
        return self.open()

    def __exit__(self, type, value, traceback) -> None:
        self.close()

    def open(self) -> Self:
        logger.info('Opening Momonga.')
        self.session_manager.open()
        time.sleep(self.internal_xmit_interval)
        self.is_open = True
        self.__init_energy_unit()
        logger.info('Momonga is open.')
        return self

    def close(self) -> None:
        logger.info('Closing Momonga.')
        self.is_open = False
        self.session_manager.close()
        logger.info('Momonga is closed.')

    def __get_transaction_id(self) -> int:
        self.transaction_id += 1
        return self.transaction_id

    @staticmethod
    def __build_request_header(tid: int, esv: EchonetServiceCode) -> bytes:
        ehd = b'\x10\x81'  # echonet lite edata format 1
        tid = tid.to_bytes(4, 'big')[-2:]
        seoj = b'\x05\xFF\x01'  # controller class
        deoj = b'\x02\x88\x01'  # low-voltage smart electric energy meter class
        esv = esv.to_bytes(1, 'big')
        return ehd + tid + seoj + deoj + esv

    def __build_request_payload_with_data(self,
                                          tid: int,
                                          esv: EchonetServiceCode,
                                          properties_with_data: list[EchonetPropertyWithData],
                                          ) -> bytes:
        header = self.__build_request_header(tid, esv)
        opc = len(properties_with_data).to_bytes(1, 'big')
        payload = header + opc
        for pd in properties_with_data:
            epc = pd.epc.to_bytes(1, 'big')
            pdc = len(pd.edt).to_bytes(1, 'big')
            edt = pd.edt
            payload += epc + pdc + edt

        return payload

    def __build_request_payload(self,
                                tid: int,
                                esv: EchonetServiceCode,
                                properties: list[EchonetProperty],
                                ) -> bytes:
        header = self.__build_request_header(tid, esv)  # get
        opc = len(properties).to_bytes(1, 'big')
        payload = header + opc
        for p in properties:
            epc = p.epc.to_bytes(1, 'big')
            pdc = b'\x00'
            payload += epc + pdc

        return payload

    @staticmethod
    def __extract_response_payload(data: bytes,
                                   tid: int,
                                   req_properties: list[EchonetPropertyWithData] | list[EchonetProperty],
                                   ) -> list[EchonetPropertyWithData]:
        ehd = data[0:2]
        if ehd != b'\x10\x81':  # echonet lite edata format 1
            raise MomongaResponseNotExpected('The data format is not ECHONET Lite EDATA format 1')

        if data[2:4] != tid.to_bytes(4, 'big')[-2:]:
            raise MomongaResponseNotExpected('The transaction ID does not match.')

        seoj = data[4:7]
        if seoj != b'\x02\x88\x01':  # low-voltage smart electric energy meter class
            raise MomongaResponseNotExpected('The source is not a smart meter.')

        deoj = data[7:10]
        if deoj != b'\x05\xFF\x01':  # controller class
            raise MomongaResponseNotExpected('The destination is not a controller.')

        esv = data[10]
        if 0x50 <= esv <= 0x5F:
            raise MomongaResponseNotPossible('The target smart meter could not respond. ESV: %X' % esv)

        opc = data[11]
        req_opc = len(req_properties)
        if opc != req_opc:
            raise MomongaResponseNotExpected(
                'Unexpected packet format. OPC is expected %s but %d was set.' % (req_opc, opc))

        properties = []
        cur = 12
        for rp in req_properties:
            try:
                epc = EchonetPropertyCode(data[cur])
            except ValueError:
                epc = data[cur]

            if epc != rp.epc:
                raise MomongaResponseNotExpected('The property code does not match. EPC: %X' % rp.epc)

            cur += 1
            pdc = data[cur]
            cur += 1
            if pdc == 0:
                edt = None
            else:
                edt_from = cur
                cur += pdc
                edt = data[edt_from:cur]

            properties.append(EchonetPropertyWithData(epc, edt))

        return properties

    def __request(self,
                  esv: EchonetServiceCode,
                  req_properties: list[EchonetPropertyWithData] | list[EchonetProperty],
                  ) -> list[EchonetPropertyWithData]:
        logger.debug('Checking if Momonga is open: is_open=%s', self.is_open)
        if self.is_open is not True:
            raise RuntimeError('Momonga is not open.')

        tid = self.__get_transaction_id()
        if esv == EchonetServiceCode.set_c:
            tx_payload = self.__build_request_payload_with_data(tid, esv, req_properties)
        elif esv == EchonetServiceCode.get:
            tx_payload = self.__build_request_payload(tid, esv, req_properties)
        else:
            raise MomongaRuntimeError('Unsupported service code.')

        while not self.session_manager.recv_q.empty():
            self.session_manager.recv_q.get()  # drops stored data

        for _ in range(self.xmit_retries):
            self.session_manager.xmitter(tx_payload)
            while True:
                try:
                    res = self.session_manager.recv_q.get(timeout=self.recv_timeout)
                except queue.Empty:
                    logger.warning('The request for transaction id "%04X" timed out.' % tid)
                    break  # to rexmit the request.

                # messages of event types 21, 02, and received udp payloads will only be delivered.
                if res.startswith('EVENT 21'):
                    param = res.split()[-1]
                    if param == '00':
                        logger.info('Successfully transmitted a request packet for transaction id "%04X".' % tid)
                        continue
                    elif param == '01':
                        logger.info('Retransmitting the request packet for transaction id "%04X".' % tid)
                        time.sleep(self.internal_xmit_interval)
                        break  # to rexmit the request.
                    elif param == '02':
                        logger.info('Transmitting neighbor solicitation packets.')
                        continue
                    else:
                        logger.debug('A message for event 21 with an unknown parameter "%s" will be ignored.' % param)
                        continue
                elif res.startswith('EVENT 02'):
                    logger.info('Received a neighbor advertisement packet.')
                    continue
                elif res.startswith('ERXUDP'):
                    udp_pkt = SkEventRxUdp([res])
                    if not (udp_pkt.src_port == udp_pkt.dst_port == 0x0E1A):
                        continue
                    elif udp_pkt.side != 0:
                        continue
                    elif udp_pkt.src_addr != self.session_manager.smart_meter_addr:
                        continue

                    try:
                        res_properties = self.__extract_response_payload(udp_pkt.data, tid, req_properties)
                    except MomongaResponseNotExpected:
                        continue

                    logger.info('Successfully received a response packet for transaction id "%04X".' % tid)
                    return res_properties
                else:
                    # this line should never be reached.
                    continue
        logger.error('Gave up to obtain a response for transaction id "%04X". Close Momonga and open it again.' % tid)
        raise MomongaNeedToReopen('Gave up to obtain a response for transaction id "%04X".'
                                  ' Close Momonga and open it again.' % tid)

    def __request_to_set(self,
                         properties_with_data: list[EchonetPropertyWithData]
                         ) -> None:
        self.__request(EchonetServiceCode.set_c, properties_with_data)

    def __request_to_get(self,
                         properties: list[EchonetProperty],
                         ) -> list[EchonetPropertyWithData]:
        return self.__request(EchonetServiceCode.get, properties)

    def get_operation_status(self) -> bool | None:
        req = EchonetProperty(EchonetPropertyCode.operation_status)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_operation_status(res.edt)

    def get_installation_location(self) -> str:
        req = EchonetProperty(EchonetPropertyCode.installation_location)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_installation_location(res.edt)

    def get_standard_version(self) -> str:
        req = EchonetProperty(EchonetPropertyCode.standard_version_information)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_standard_version_information(res.edt)

    def get_fault_status(self) -> bool | None:
        req = EchonetProperty(EchonetPropertyCode.fault_status)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_fault_status(res.edt)

    def get_manufacturer_code(self) -> bytes:
        req = EchonetProperty(EchonetPropertyCode.manufacturer_code)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_manufacturer_code(res.edt)

    def get_serial_number(self) -> str:
        req = EchonetProperty(EchonetPropertyCode.serial_number)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_serial_number(res.edt)

    def get_current_time_setting(self) -> datetime.time:
        req = EchonetProperty(EchonetPropertyCode.current_time_setting)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_current_time_setting(res.edt)

    def get_current_date_setting(self) -> datetime.date:
        req = EchonetProperty(EchonetPropertyCode.current_date_setting)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_current_date_setting(res.edt)

    def get_properties_for_status_notification(self) -> set[EchonetPropertyCode | int]:
        req = EchonetProperty(EchonetPropertyCode.properties_for_status_notification)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_property_map(res.edt)

    def get_properties_to_set_values(self) -> set[EchonetPropertyCode | int]:
        req = EchonetProperty(EchonetPropertyCode.properties_to_set_values)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_property_map(res.edt)

    def get_properties_to_get_values(self) -> set[EchonetPropertyCode | int]:
        req = EchonetProperty(EchonetPropertyCode.properties_to_get_values)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_property_map(res.edt)

    def get_route_b_id(self) -> dict[str, bytes]:
        req = EchonetProperty(EchonetPropertyCode.route_b_id)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_route_b_id(res.edt)

    def get_one_minute_measured_cumulative_energy(self) -> dict[str, datetime.datetime |
                                                                     dict[str, int | float | None]]:
        req = EchonetProperty(EchonetPropertyCode.one_minute_measured_cumulative_energy)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_one_minute_measured_cumulative_energy(res.edt,
                                                                             self.energy_unit,
                                                                             self.energy_coefficient)

    def get_coefficient_for_cumulative_energy(self) -> int:
        req = EchonetProperty(EchonetPropertyCode.coefficient_for_cumulative_energy)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_coefficient_for_cumulative_energy(res.edt)

    def get_number_of_effective_digits_for_cumulative_energy(self) -> int:
        req = EchonetProperty(EchonetPropertyCode.number_of_effective_digits_for_cumulative_energy)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_number_of_effective_digits_for_cumulative_energy(res.edt)

    def get_measured_cumulative_energy(self,
                                       reverse: bool = False,
                                       ) -> int | float:
        if reverse is False:
            epc = EchonetPropertyCode.measured_cumulative_energy
        else:
            epc = EchonetPropertyCode.measured_cumulative_energy_reversed

        req = EchonetProperty(epc)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_measured_cumulative_energy(res.edt,
                                                                  self.energy_unit,
                                                                  self.energy_coefficient)

    def get_unit_for_cumulative_energy(self) -> int | float:
        req = EchonetProperty(EchonetPropertyCode.unit_for_cumulative_energy)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_unit_for_cumulative_energy(res.edt)

    def get_historical_cumulative_energy_1(self,
                                           day: int = 0,
                                           reverse: bool = False,
                                           ) -> list[dict[str, datetime.datetime | dict[str, int | float | None]]]:
        self.set_day_for_historical_data_1(day)

        if reverse is False:
            epc = EchonetPropertyCode.historical_cumulative_energy_1
        else:
            epc = EchonetPropertyCode.historical_cumulative_energy_1_reversed

        req = EchonetProperty(epc)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_historical_cumulative_energy_1(res.edt,
                                                                      self.energy_unit,
                                                                      self.energy_coefficient)

    def set_day_for_historical_data_1(self,
                                      day: int = 0,
                                      ) -> None:
        edt = EchonetDataBuilder.build_edata_to_set_day_for_historical_data_1(day)
        req = EchonetPropertyWithData(EchonetPropertyCode.day_for_historical_data_1, edt)
        self.__request_to_set([req])

    def get_day_for_historical_data_1(self) -> int:
        req = EchonetProperty(EchonetPropertyCode.day_for_historical_data_1)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_day_for_historical_data_1(res.edt)

    def get_instantaneous_power(self) -> float:
        req = EchonetProperty(EchonetPropertyCode.instantaneous_power)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_instantaneous_power(res.edt)

    def get_instantaneous_current(self) -> dict[str, float]:
        req = EchonetProperty(EchonetPropertyCode.instantaneous_current)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_instantaneous_current(res.edt)

    def get_cumulative_energy_measured_at_fixed_time(self,
                                                     reverse: bool = False,
                                                     ) -> dict[str, datetime.datetime | int | float]:
        if reverse is False:
            epc = EchonetPropertyCode.cumulative_energy_measured_at_fixed_time
        else:
            epc = EchonetPropertyCode.cumulative_energy_measured_at_fixed_time_reversed

        req = EchonetProperty(epc)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_cumulative_energy_measured_at_fixed_time(res.edt,
                                                                                self.energy_unit,
                                                                                self.energy_coefficient)

    def get_historical_cumulative_energy_2(self,
                                           timestamp: datetime.datetime = None,
                                           num_of_data_points: int = 12,
                                           ) -> list[dict[str, datetime.datetime |
                                                               dict[str, int | float | None]]]:
        if timestamp is None:
            timestamp = datetime.datetime.now()

        self.set_time_for_historical_data_2(timestamp, num_of_data_points)

        req = EchonetProperty(EchonetPropertyCode.historical_cumulative_energy_2)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_historical_cumulative_energy_2(res.edt,
                                                                      self.energy_unit,
                                                                      self.energy_coefficient)

    def set_time_for_historical_data_2(self,
                                       timestamp: datetime.datetime,
                                       num_of_data_points: int = 12,
                                       ) -> None:
        edt = EchonetDataBuilder.build_edata_to_set_time_for_historical_data_2(timestamp,
                                                                               num_of_data_points)
        req = EchonetPropertyWithData(EchonetPropertyCode.time_for_historical_data_2, edt)
        self.__request_to_set([req])

    def get_time_for_historical_data_2(self) -> dict[str: datetime.datetime | None,
                                                     str: int]:
        req = EchonetProperty(EchonetPropertyCode.time_for_historical_data_2)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_time_for_historical_data_2(res.edt)

    def get_historical_cumulative_energy_3(self,
                                           timestamp: datetime.datetime = None,
                                           num_of_data_points: int = 10,
                                           ) -> list[dict[str, datetime.datetime |
                                                               dict[str, int | float | None]]]:
        if timestamp is None:
            timestamp = datetime.datetime.now()

        self.set_time_for_historical_data_3(timestamp, num_of_data_points)

        req = EchonetProperty(EchonetPropertyCode.historical_cumulative_energy_3)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_historical_cumulative_energy_3(res.edt,
                                                                      self.energy_unit,
                                                                      self.energy_coefficient)

    def set_time_for_historical_data_3(self,
                                       timestamp: datetime.datetime,
                                       num_of_data_points: int = 10,
                                       ) -> None:
        edt = EchonetDataBuilder.build_edata_to_set_time_for_historical_data_3(timestamp,
                                                                               num_of_data_points)
        req = EchonetPropertyWithData(EchonetPropertyCode.time_for_historical_data_3, edt)
        self.__request_to_set([req])

    def get_time_for_historical_data_3(self) -> dict[str, datetime.datetime | None | int]:
        req = EchonetProperty(EchonetPropertyCode.time_for_historical_data_3)
        res = self.__request_to_get([req])[0]
        return EchonetDataParser.parse_time_for_historical_data_3(res.edt)

    class DayForHistoricalData1(TypedDict, total=False):
        day: int

    class TimeForHistoricalData2(TypedDict, total=False):
        timestamp: datetime.datetime
        num_of_data_points: int

    class TimeForHistoricalData3(TypedDict, total=False):
        timestamp: datetime.datetime
        num_of_data_points: int

    def request_to_set(self,
                       day_for_historical_data_1: DayForHistoricalData1 | None = None,
                       time_for_historical_data_2: TimeForHistoricalData2 | None = None,
                       time_for_historical_data_3: TimeForHistoricalData3 | None = None) -> None:
        properties_with_data = []
        if day_for_historical_data_1 is not None:
            edt = EchonetDataBuilder.build_edata_to_set_day_for_historical_data_1(**day_for_historical_data_1)
            properties_with_data.append(EchonetPropertyWithData(EchonetPropertyCode.day_for_historical_data_1, edt))
        if time_for_historical_data_2 is not None:
            edt = EchonetDataBuilder.build_edata_to_set_time_for_historical_data_2(**time_for_historical_data_2)
            properties_with_data.append(EchonetPropertyWithData(EchonetPropertyCode.time_for_historical_data_2, edt))
        if time_for_historical_data_3 is not None:
            edt = EchonetDataBuilder.build_edata_to_set_time_for_historical_data_3(**time_for_historical_data_3)
            properties_with_data.append(EchonetPropertyWithData(EchonetPropertyCode.time_for_historical_data_3, edt))

        self.__request_to_set(properties_with_data)

    def request_to_get(self,
                       properties: set[EchonetPropertyCode]) -> dict[EchonetPropertyCode, Any]:
        results = self.__request_to_get([EchonetProperty(epc) for epc in properties])
        parsed_results = {}
        for r in results:
            try:
                parser = parser_map[r.epc]
            except KeyError:
                raise MomongaRuntimeError(f"No parser found for EPC: %X" % r.epc)

            sig = inspect.signature(parser)
            args = sig.parameters.keys()
            if "energy_unit" in args and "energy_coefficient" in args:
                parsed_results[r.epc] = parser(r.edt, self.energy_unit, self.energy_coefficient)
            else:
                parsed_results[r.epc] = parser(r.edt)

        return parsed_results
