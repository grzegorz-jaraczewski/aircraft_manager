# Third party imports
import pytest
from unittest.mock import patch, Mock

# Internal imports
from src.schemas import (InputAircraftPerformanceEnduranceSchema,
                         InputAircraftPerformanceRangeSchema,
                         OutputAircraftPerformanceEnduranceSchema,
                         OutputAircraftPerformanceRangeSchema)
from src.use_cases.performance import Performance
from tests.conftest import db_session, load_data


class TestPerformance:

    @pytest.fixture
    @patch('src.schemas.InputAircraftPerformanceRangeSchema')
    def mock_input_aircraft_performance_range_schema(self, mock_schema):
        mock_schema.return_value = InputAircraftPerformanceRangeSchema(aircraft_id=100, wind_speed=10.0, fuel=60.0)
        return mock_schema.return_value

    @pytest.fixture
    def mock_output_aircraft_performance_range_schema(self, mocker):
        return mocker.patch('src.schemas.OutputAircraftPerformanceRangeSchema',
                            OutputAircraftPerformanceRangeSchema(name='C-152', range=800.0))

    @pytest.fixture
    def mock_input_aircraft_performance_endurance_schema(self, mocker):
        return mocker.patch('src.schemas.InputAircraftPerformanceEnduranceSchema',
                            InputAircraftPerformanceEnduranceSchema(aircraft_id=100, fuel=60.0))

    @pytest.fixture
    def mock_output_aircraft_performance_endurance_schema(self, mocker):
        return mocker.patch('src.schemas.OutputAircraftPerformanceEnduranceSchema',
                            OutputAircraftPerformanceEnduranceSchema(name='C-152', endurance='04:00'))

    def test_calculate_range(self, mock_input_aircraft_performance_range_schema,
                             mock_output_aircraft_performance_range_schema, load_data, db_session):
        output = Performance(db_session).calculate_range(
            input_data=mock_input_aircraft_performance_range_schema)

        expected_output = mock_output_aircraft_performance_range_schema

        assert output == expected_output
        assert output.name == 'C-152'
        assert output.range == 800.0

    def test_calculate_range_2(self, mock_input_aircraft_performance_range_schema):
        mock_session = Mock()
        performance = Performance(mock_session)

        mock_aircraft = Mock()
        mock_aircraft.name = 'C-152'

        mock_aircraft_data = Mock()
        mock_aircraft_data.cruise_speed = 190
        mock_aircraft_data.fuel_consumption = 15

        mock_session.query.return_value.filter_by.return_value.first.side_effect = [
            mock_aircraft, mock_aircraft_data]
        result = performance.calculate_range(mock_input_aircraft_performance_range_schema)

        assert isinstance(result, OutputAircraftPerformanceRangeSchema)
        assert result.name == 'C-152'
        assert result.range == 800

    def test_calculate_endurance(self, mock_input_aircraft_performance_endurance_schema,
                                 mock_output_aircraft_performance_endurance_schema, load_data, db_session):
        output = Performance(db_session).calculate_endurance(
            input_data=mock_input_aircraft_performance_endurance_schema)

        expected_output = mock_output_aircraft_performance_endurance_schema

        assert output == expected_output
        assert output.name == 'C-152'
        assert output.endurance == '04:00'

    def test_calculate_endurance_2(self, mock_input_aircraft_performance_endurance_schema):
        mock_session = Mock()
        performance = Performance(mock_session)

        mock_aircraft = Mock()
        mock_aircraft.name = 'C-152'

        mock_aircraft_data = Mock()
        mock_aircraft_data.fuel_consumption = 15

        mock_session.query.return_value.filter_by.return_value.first.side_effect = [
            mock_aircraft, mock_aircraft_data]

        result = performance.calculate_endurance(input_data=mock_input_aircraft_performance_endurance_schema)

        assert isinstance(result, OutputAircraftPerformanceEnduranceSchema)
        assert result.name == 'C-152'
        assert result.endurance == '04:00'
