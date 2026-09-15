from app.services import ambulance_equipment_requirements


def test_hospital_only_requirements_do_not_block_ambulance_matching():
    assert ambulance_equipment_requirements({"ICU", "VENTILATOR", "TRAUMA"}) == {
        "VENTILATOR",
        "TRAUMA_KIT",
    }
