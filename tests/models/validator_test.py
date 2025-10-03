from unittest.mock import MagicMock

import pytest
from bson import ObjectId

from app.models.reporte import Reporte
from app.models.validator import Validator
from tests.mock_data import get_mock_report

month = "2024-01"
validator = Validator()

mock_db_report = {
    "month": "2024-01",
    "department": ObjectId("670d497acc1f3bec1f22a795")
}

mock_location = {
    "dpto": "Arauca",
    "ward": ["gineco"],
    "ward_type": []
}


@pytest.fixture
def mock_mongo(mocker):
    mock = mocker.patch("app.db.Database", autoSpec=True)
    mock.return_value.get_collection.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_request(mocker):
    mock = mocker.patch("flask.request")
    return mock


class TestValidator:

    @staticmethod
    def test_validate_country_error():
        mock_report = get_mock_report()
        mock_report["COUNTRY_A"] = "MEX"

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert len(errors.values()) == 1
        assert errors["COUNTRY_A"] == "COUNTRY_A debe ser COL"

    @staticmethod
    def test_validate_pad_type_new_error():
        mock_report = get_mock_report()
        mock_report["PAT_TYPE"] = "new"
        mock_report["AGE"] = "2m"
        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert len(errors.values()) == 1
        assert errors["PAT_TYPE"] == "PAT_TYPE no coincide con el rango de edad"

    @staticmethod
    def test_validate_pad_type_ped_error():
        mock_report = get_mock_report()
        mock_report["PAT_TYPE"] = "ped"
        mock_report["AGE"] = "2d"
        reporte = Reporte(mock_report)

        errors = reporte.validate(mock_db_report)

        assert len(errors.values()) == 1
        assert errors["PAT_TYPE"] == "PAT_TYPE no coincide con el rango de edad"

    @staticmethod
    def test_validate_pad_type_adu_error():
        mock_report = get_mock_report()
        mock_report["PAT_TYPE"] = "adu"
        mock_report["AGE"] = "17"
        reporte = Reporte(mock_report)

        errors = reporte.validate(mock_db_report)

        assert len(errors.values()) == 1
        assert errors["PAT_TYPE"] == "PAT_TYPE no coincide con el rango de edad"

    @staticmethod
    def test_validate_pad_type_ok(

    ):
        mock_report = get_mock_report()
        mock_report["PAT_TYPE"] = "ped"
        mock_report["AGE"] = "2m"
        reporte = Reporte(mock_report)

        errors = reporte.validate(mock_db_report)

        assert len(errors.values()) == 0

    @staticmethod
    def test_should_return_error_when_country_a_is_empty():
        mock_report = get_mock_report()
        mock_report["COUNTRY_A"] = None
        mock_report["PAT_TYPE"] = "ped"
        mock_report["AGE"] = "1m"
        reporte = Reporte(mock_report)

        errors = reporte.validate(mock_db_report)

        assert errors["COUNTRY_A"] == "COUNTRY_A debe ser COL"
        assert len(errors.values()) == 1

    @staticmethod
    def test_should_laboratory_equals_to_institut():
        mock_report = get_mock_report()
        mock_report["LABORATORY"] = "a"
        mock_report["INSTITUT"] = "b"
        reporte = Reporte(mock_report)

        errors = reporte.validate(mock_db_report)

        assert errors["LABORATORY"] == "LABORATORY debe ser igual a INSTITUT"
        assert errors["INSTITUT"] == "INSTITUT debe ser igual a LABORATORY"
        assert len(errors.values()) == 2

    @staticmethod
    def test_should_sex_be_m_or_f():
        mock_report = get_mock_report()
        mock_report["SEX"] = "x"

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert errors["SEX"] == "SEX debe ser M o F"
        assert len(errors.values()) == 1

    @staticmethod
    def test_should_age_throw_error_if_is_over_100():
        mock_report = get_mock_report()
        mock_report["AGE"] = "101"

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert errors["AGE"] == "AGE debe ser menor a 100"
        assert len(errors.values()) == 1

    @staticmethod
    def test_should_return_error_when_age_is_zero():
        mock_report = get_mock_report()
        mock_report["AGE"] = 0

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert errors["AGE"] == "DATE_BIRTH no puede ser vacía"
        assert errors["PAT_TYPE"] == "PAT_TYPE no coincide con el rango de edad"
        assert len(errors.values()) == 2

    @staticmethod
    def test_should_return_error_when_van_nm_is_greater_than_4():
        mock_report = get_mock_report()
        mock_report["VAN_NM"] = ">4"

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert errors["VAN_NM"] == "VAN_NM no puede ser >4"
        assert len(errors.values()) == 1

    @staticmethod
    def test_should_return_error_when_birthdate_is_invalid():
        mock_report = get_mock_report()
        mock_report["DATE_BIRTH"] = "aaaa"

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert errors["DATE_BIRTH"] == "DATE_BIRTH debe ser una fecha válida"
        assert len(errors.values()) == 1

    @staticmethod
    def test_should_return_error_when_ward_is_uci_ad_and_age_is_below_18(
            mock_mongo: any
    ):
        mock_mongo.get_collection("locations").find_one.return_value = mock_location

        mock_report = get_mock_report()
        mock_report["WARD"] = "uci ad"
        mock_report["AGE"] = 17

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert errors["WARD"] == "WARD no puede ser uci ad"
        assert len(errors) == 2

    @staticmethod
    def test_should_return_error_when_ward_is_ucipe_and_age_in_invalid_range():
        mock_report = get_mock_report()
        mock_report["WARD"] = "ucine"
        mock_report["AGE"] = "15d"

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert errors["PAT_TYPE"] == "PAT_TYPE no coincide con el rango de edad"
        assert len(errors) == 1

    @staticmethod
    def test_should_return_error_when_ward_is_ucine_and_age_above_threshold():
        mock_report = get_mock_report()
        mock_report["WARD"] = "ucine"
        mock_report["AGE"] = 0.1

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert errors["WARD"] == "WARD no puede ser ucine"
        assert errors["PAT_TYPE"] == "PAT_TYPE no coincide con el rango de edad"
        assert len(errors) == 2

    @staticmethod
    def test_should_not_return_errors_when_spec_type_is_valid():
        mock_report = get_mock_report()
        mock_report["WARD"] = "ucipe"
        mock_report["AGE"] = "19"

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert errors["WARD"] == "WARD no puede ser ucipe"
        assert len(errors) == 1

    @staticmethod
    def test_should_not_return_errors_when_conditions_not_met():
        mock_report = get_mock_report()
        mock_report["WARD"] = "uci ad"
        mock_report["AGE"] = 20

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert "WARD" not in errors
        assert len(errors) == 0

    @staticmethod
    def test_should_return_error_when_spec_type_is_not_found(
            mock_mongo: any
    ):
        mock_mongo.get_collection("samples").find_one.return_value = None

        mock_report = get_mock_report()
        mock_report["SPEC_TYPE"] = "no_existe"

        reporte = Reporte(mock_report)
        reporte.db = mock_mongo
        errors = reporte.validate(mock_db_report)

        assert errors["SPEC_TYPE"] == "SPEC_TYPE no encontrado"
        assert len(errors) == 1

    @staticmethod
    def test_should_return_error_when_spec_type_is_invalid(
            mock_mongo: any
    ):
        mock_mongo.get_collection("samples").find_one.return_value = {
            "value": "Boca"
        }

        mock_report = get_mock_report()
        mock_report["SPEC_TYPE"] = "bo"
        mock_report["LOCAL_SPEC"] = "Ojos"

        reporte = Reporte(mock_report)
        reporte.db = mock_mongo
        errors = reporte.validate(mock_db_report)

        assert errors["LOCAL_SPEC"] == "LOCAL_SPEC no es correcto, debería ser Boca"
        assert len(errors) == 1

    @staticmethod
    def test_should_add_error_if_spec_date_not_match():
        _month = "2024-05"

        mock_report = get_mock_report()
        mock_db_report["month"] = "2024-05"

        reporte = Reporte(mock_report)
        errors = reporte.validate(mock_db_report)

        assert errors["SPEC_DATE"] == "SPEC_DATE no coincide con el mes seleccionado - 2024-05"
        assert len(errors) == 1

