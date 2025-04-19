from c3hm.core.omnivox import extract_student_info


def test_extract_student_info():
    assert extract_student_info("NOM1_NOM2_12345") == "NOM1_NOM2_12345"
    assert extract_student_info("NOM1_NOM2_12345_") == "NOM1_NOM2_12345"
    assert extract_student_info("NOM1_NOM2_12345_67890") == "NOM1_NOM2_12345"
    assert extract_student_info("12345_67890_") is None
    assert extract_student_info("NOM1_12345_67890") == "NOM1_12345"
    assert extract_student_info("NOM1") is None

