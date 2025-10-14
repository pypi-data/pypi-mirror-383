from enum import Enum, EnumMeta

__all__ = ["enum_of_dataclass_factory"]


def enum_of_dataclass_factory(target_data_class):
    """
    Factory of Enums that only accept a specific Dataclass object as enum elements

    :param target_data_class: the dataclass that will be accepted as Enum value
    :return: the Enum object enforcing a check on enum values
    """

    class EnumOfDataclassMeta(EnumMeta):
        def __new__(mcs, cls, bases, classdict, **kwargs):  # noqa: B902
            new_enum = super().__new__(mcs, cls, bases, classdict, **kwargs)
            for el in new_enum:
                if not isinstance(el.value, target_data_class):
                    raise ValueError(f"{el.name} is not a valid {target_data_class}")
            return new_enum

    EnumOfDataclassMeta.__name__ = f"EnumOf{target_data_class}Meta"

    class EnumOfDataclass(Enum, metaclass=EnumOfDataclassMeta):
        pass

    EnumOfDataclass.__name__ = f"EnumOf{target_data_class}"
    return EnumOfDataclass
