from src.multibunch_feedback_applications.Common import reconfigure_to_lists


def test_reconfigure_to_lists_output_correct_type():
    test_input = [
        {"data1": 11, "data2": 22},
        {"data1": 33, "data2": 44},
        {"data1": 55, "data2": 66},
    ]
    output = reconfigure_to_lists(test_input)
    assert type(output) is dict
    assert output.keys == ["data1", "data2"]
