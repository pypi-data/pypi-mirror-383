from aleksis.core.mixins import RegistryObject


def test_registry_object_name():
    class ExampleRegistry(RegistryObject):
        pass

    class ExampleWithManualName(ExampleRegistry):
        _class_name = "example_a"

    class ExampleWithAutomaticName(ExampleRegistry):
        pass

    class ExampleWithOverridenAutomaticName(ExampleWithManualName):
        _class_name = "example_b"

    class ExampleWithOverridenManualName(ExampleWithAutomaticName):
        _class_name = "example_bb"

    assert ExampleRegistry._class_name == ""
    assert ExampleWithManualName._class_name == "example_a"
    assert ExampleWithAutomaticName._class_name == "ExampleWithAutomaticName"
    assert ExampleWithOverridenAutomaticName._class_name == "example_b"
    assert ExampleWithOverridenManualName._class_name == "example_bb"


def test_registry_object_registry():
    class ExampleRegistry(RegistryObject):
        pass

    class ExampleA(ExampleRegistry):
        pass

    class ExampleB(ExampleRegistry):
        pass

    class ExampleAA(ExampleA):
        _class_name = "example_aa"

    assert ExampleRegistry.registered_objects_dict == {
        "ExampleA": ExampleA,
        "ExampleB": ExampleB,
        "example_aa": ExampleAA,
    }
    assert ExampleRegistry.registered_objects_dict == ExampleRegistry._registry

    assert ExampleRegistry.registered_objects_list == [
        ExampleA,
        ExampleB,
        ExampleAA,
    ]

    assert ExampleRegistry.get_object_by_name("ExampleA") == ExampleA
    assert ExampleRegistry.get_object_by_name("ExampleB") == ExampleB
    assert ExampleRegistry.get_object_by_name("example_aa") == ExampleAA
