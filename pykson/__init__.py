from enum import Enum
from typing import Dict, Any, Tuple, List, Optional, TypeVar, Union, Type, Set
import six
import json

name = "pykson"


class FieldType(Enum):
    INTEGER = 1
    FLOAT = 2
    BOOLEAN = 3
    STRING = 4
    LIST = 5


class Field:

    # noinspection PyProtectedMember
    def __get__(self, instance, owner):
        if instance is None:
            raise Exception('Cannot access field without instance')
        return instance._data[self.serialized_name]

    # noinspection PyProtectedMember
    def __set__(self, instance, value):
        if not self.null:
            assert value is not None, "Null value for not nullable field: " + self.serialized_name
        if instance is None:
            raise Exception('Cannot access field without instance')
        instance._data[self.serialized_name] = value

    def __init__(self, field_type: FieldType, serialized_name: Optional[str] = None, null: bool = True):
        self.field_type = field_type
        self.serialized_name = serialized_name  # field name in serialized json
        self.name = None  # field name in the defined class
        self.null = null


class IntegerField(Field):

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, int):
            raise TypeError(instance, self.name, int, value)
        super().__set__(instance, value)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True):
        super(IntegerField, self).__init__(field_type=FieldType.INTEGER, serialized_name=serialized_name, null=null)


class FloatField(Field):

    def __set__(self, instance, value):
        if value is not None and isinstance(value,int):
            value=float(value)
        if value is not None and not isinstance(value, float):
            raise TypeError(instance, self.name, float, value)
        super().__set__(instance, value)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True):
        super(FloatField, self).__init__(field_type=FieldType.FLOAT, serialized_name=serialized_name, null=null)


class BooleanField(Field):

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, bool):
            raise TypeError(instance, self.name, bool, value)
        super().__set__(instance, value)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True):
        super(BooleanField, self).__init__(field_type=FieldType.BOOLEAN, serialized_name=serialized_name, null=null)


class StringField(Field):

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, str):
            raise TypeError(instance, self.name, str, value)
        super().__set__(instance, value)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True):
        super(StringField, self).__init__(field_type=FieldType.STRING, serialized_name=serialized_name, null=null)


class MultipleChoiceStringField(Field):

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, str):
            raise TypeError(instance, self.name, str, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value '+str(value)+' not present in options ' + str(self.options))
        super().__set__(instance, value)

    def __init__(self, options: Union[List[str], Set[str]], serialized_name: Optional[str] = None, null: bool = True):
        super(MultipleChoiceStringField, self).__init__(field_type=FieldType.STRING, serialized_name=serialized_name, null=null)
        if options is None:
            raise Exception("Null options passed for multiple choice string field")
        if not (isinstance(options, list) or isinstance(options, set)):
            raise Exception("Invalid type for options passed for multiple choice string field, must be either set or list but found " + str(type(options)) )
        if len(options) == 0:
            raise Exception("Empty options passed for enum string field")
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of multiple choice string field")
        for option in options:
            if not isinstance(option, str):
                raise Exception("Invalid value in options of multiple choice string field, " + str(option) + ', expected str value but found ' + str(type(option)))
        self.options = set(options)


class EnumStringField(Field):

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, str):
            raise TypeError(instance, self.name, str, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value '+str(value)+' not present in enum values ' + str(self.options))
        super().__set__(instance, value)

    def __init__(self, enum, serialized_name: Optional[str] = None, null: bool = True):
        super(EnumStringField, self).__init__(field_type=FieldType.STRING, serialized_name=serialized_name, null=null)
        if enum is None:
            raise Exception("Null enum passed for enum string field")
        if not issubclass(enum, Enum):
            raise Exception("Passed enum class must be a subclass of Enum")
        options = [e.value for e in enum]
        if len(options) == 0:
            raise Exception("Enum with no values for enum string field")
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of enum string field")
        for option in options:
            if not isinstance(option, str):
                raise Exception("Invalid value in enum string field, " + str(option) + ', expected str value but found ' + str(type(option)))
        self.enum = enum
        self.options = set(options)


class MultipleChoiceIntegerField(Field):

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, int):
            raise TypeError(instance, self.name, int, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value '+str(value)+' not present in options ' + str(self.options))
        super().__set__(instance, value)

    def __init__(self, options: Union[List[int], Set[int]], serialized_name: Optional[str] = None, null: bool = True):
        super(MultipleChoiceIntegerField, self).__init__(field_type=FieldType.INTEGER, serialized_name=serialized_name, null=null)
        if options is None:
            raise Exception("Null options passed for multiple choice integer field")
        if not (isinstance(options, list) or isinstance(options, set)):
            raise Exception("Invalid type for options passed for multiple choice integer field, must be either set or list but found " + str(type(options)))
        if len(options) == 0:
            raise Exception("Empty options passed for multiple choice integer field")
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of multiple choice integer field")
        for option in options:
            if not isinstance(option, int):
                raise Exception("Invalid value in options of multiple choice integer field, " + str(option) + ', expected int value but found ' + str(type(option)))
        self.options = set(options)


class EnumIntegerField(Field):

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, int):
            raise TypeError(instance, self.name, int, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value '+str(value)+' not present in enum values ' + str(self.options))
        super().__set__(instance, value)

    def __init__(self, enum, serialized_name: Optional[str] = None, null: bool = True):
        super(EnumIntegerField, self).__init__(field_type=FieldType.INTEGER, serialized_name=serialized_name, null=null)
        if enum is None:
            raise Exception("Null enum passed for enum string field")
        if not issubclass(enum, Enum):
            raise Exception("Passed enum class must be a subclass of Enum")
        options = [e.value for e in enum]
        if len(options) == 0:
            raise Exception("Enum with no values passed for enum integer field")
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of enum integer field")
        for option in options:
            if not isinstance(option, int):
                raise Exception("Invalid value in enum integer field, " + str(option) + ', expected int value but found ' + str(type(option)))
        self.options = set(options)

F = TypeVar('F', bound=Field)


class ListField(Field):

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, list):
            raise TypeError(instance, self.name, list, value)
        if value is None:
            value = []
        for item in value:
            assert item is not None, "Null item passed to ListField"
            assert isinstance(item, self.item_type), "ListField items must be of " + str(self.item_type) + ", found " + str(type(item))
        super().__set__(instance, value)

    def __init__(self, item_type: Type, serialized_name: Optional[str] = None, null: bool = True):
        super(ListField, self).__init__(field_type=FieldType.LIST, serialized_name=serialized_name, null=null)
        valid_types = [int, str, bool, float]
        assert item_type in valid_types, 'Invalid list item type ' + str(item_type) + 'must be in ' + str(valid_types)
        self.item_type = item_type


class JsonObjectMeta(type):
    # noinspection PyInitNewSignature,PyUnresolvedReferences,PyTypeChecker,SpellCheckingInspection,PyMethodParameters
    def __new__(cls, name, bases, attrs: Dict[str, Any]):
        m_module = attrs.pop('__module__')
        new_attrs = {'__module__': m_module}
        class_cell = attrs.pop('__classcell__', None)
        if class_cell is not None:
            new_attrs['__classcell__'] = class_cell

        new_class = super(JsonObjectMeta, cls).__new__(cls, name, bases, new_attrs)

        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta

        for field_name, field in attrs.items():
            if isinstance(field, Field):
                if field.serialized_name is None:
                    field.serialized_name = field_name
                field.name = field_name
                setattr(new_class, field.name, field)
            else:
                setattr(new_class, field_name, field)

        # noinspection PyUnusedLocal
        def my_custom_init(instance_self, accept_unknown: bool = False, *init_args, **init_kwargs):
            instance_self._data = {}  # dict.fromkeys(attrs.keys())
            tmp_class_dict = instance_self.__class__.__dict__
            model_field_names = [k for k in tmp_class_dict.keys() if isinstance(tmp_class_dict.get(k), Field)]
            for key, value in init_kwargs.items():
                if key in model_field_names:
                    setattr(instance_self, key, value)
                elif not accept_unknown:
                    raise Exception("value given in instance initialization but was not defined in model as Field. key:" + str(key) +
                                    " val:" + str(value) + " type(value):" + str(type(value)))

        new_class.__init__ = my_custom_init
        return new_class


class JsonObject(six.with_metaclass(JsonObjectMeta)):
    # noinspection PyUnusedLocal
    def __init__(self, accept_unknown: bool = False, *args, **kwargs):
        super(JsonObject, self).__init__()
        field_names = []
        _setattr = setattr

        # Note: maybe ? save all timestamps as utc in database. Convert them to appropriate timezones when needed in python.
        #       By default, InfluxDB stores and returns timestamps in UTC.
        #
        # influx has timezones:
        # https://docs.influxdata.com/influxdb/v1.7/query_language/data_exploration/#the-time-zone-clause
        # I tested and it supports timezones. But there is something wrong with python client.
        # >>> If I give a datetime with timezone to python client, it still stores it in db with utc.
        #     the time is not wrong but it when u query that data point again,
        #     it does not give it with the timezone we gave it in first place.
        #
        #
        # I think it is better to save times in utc and then convert it on client side (python).
        # because when I insert a point from python influx client with timezone offset (+03:30 for example),
        # it gets saved in the database as a utc. see:
        # https://stackoverflow.com/questions/39736238/how-to-set-time-zone-in-influxdb-using-python-client
        #

        fields_iter = JsonObject.get_fields(type(self))
        for field in fields_iter:
            if not field.null and kwargs.get(field.name, None) is None:
                raise ValueError("Null value passed for non-nullable field " + str(field.name))
            field_names.append(field.name)

        if kwargs:
            for prop in tuple(kwargs):
                if prop in field_names:
                    _setattr(self, prop, kwargs[prop])
                    del kwargs[prop]

        if kwargs and accept_unknown:
            raise TypeError("'%s' is an invalid keyword argument for this function" % list(kwargs)[0])

    @staticmethod
    def get_fields_mapped_by_names(cls) -> Dict[str, Field]:
        result_dict = {}
        fields_list = JsonObject.get_fields(cls)
        for field_item in fields_list:
            result_dict[field_item.name] = field_item
        return result_dict

    @staticmethod
    def get_fields_mapped_by_serialized_names(cls) -> Dict[str, Field]:
        result_dict = {}
        fields_list = JsonObject.get_fields(cls)
        for field_item in fields_list:
            if field_item.serialized_name is not None:
                result_dict[field_item.serialized_name] = field_item
            else:
                result_dict[field_item.name] = field_item
        return result_dict

    @staticmethod
    def get_field_names_mapped_by_serialized_names(cls) -> Dict[str, str]:
        result_dict = {}
        fields_list = JsonObject.get_fields(cls)
        for field_item in fields_list:
            if field_item.serialized_name is not None:
                result_dict[field_item.serialized_name] = field_item.name
        return result_dict

    @staticmethod
    def get_fields(cls) -> List[Field]:
        fields_list = []
        type_dicts = cls.__dict__  # type(self).__dict__
        for name, field in type_dicts.items():
            if isinstance(field, Field):
                fields_list.append(field)
        return fields_list

    def get_field_values_as_dict(self) -> Dict[str, Any]:
        fields_dict = {}
        type_dicts = type(self).__dict__
        for name, field in type_dicts.items():
            if isinstance(field, Field):
                field_name = field.name
                field_serialized_name = field.serialized_name
                field_value = self.__getattribute__(field_name)
                fields_dict[field_serialized_name] = field_value
        return fields_dict


T = TypeVar('T', bound=JsonObject)


class ObjectListField(Field):

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, list):
            raise TypeError(instance, self.name, list, value)
        if value is None:
            value = []
        for item in value:
            assert item is not None, "Null item passed to ObjectListField"
            assert isinstance(item, self.item_type), "ObjectListField items must be of " + str(self.item_type) + ", found " + str(type(item))
        super().__set__(instance, value)

    def __init__(self, item_type: Type[T], serialized_name: Optional[str] = None, null: bool = True):
        super(ObjectListField, self).__init__(field_type=FieldType.LIST, serialized_name=serialized_name, null=null)
        self.item_type = item_type


class Pykson:

    # noinspection PyCallingNonCallable
    @staticmethod
    def from_json(data: Union[str, Dict], cls: Type[T], accept_unknown: bool = False) -> T:
        if isinstance(data, str):
            data = json.loads(data)
        fields_mapped_by_serialized_names = JsonObject.get_fields_mapped_by_serialized_names(cls)
        field_names_mapped_by_serialized_names = JsonObject.get_field_names_mapped_by_serialized_names(cls)
        data_copy = {}
        for data_key, data_value in data.items():
            if isinstance(data_value, list) and (data_key in fields_mapped_by_serialized_names.keys()) and (isinstance(fields_mapped_by_serialized_names[data_key], ObjectListField)):
                data_list_value = []
                for data_value_item in data_value:
                    # noinspection PyUnresolvedReferences
                    data_list_value.append(
                        Pykson.from_json(data_value_item, fields_mapped_by_serialized_names[data_key].item_type)
                    )
                data_copy[data_key] = data_list_value
            else:
                if data_key in field_names_mapped_by_serialized_names.keys():
                    data_copy[field_names_mapped_by_serialized_names[data_key]] = data_value
                else:
                    data_copy[data_key] = data_value
        return cls(accept_unknown=accept_unknown, **data_copy)

    @staticmethod
    def to_json(item: T) -> str:
        fields_dict = item.get_field_values_as_dict()
        final_dict = {}
        for field_key, field_value in fields_dict.items():
            if isinstance(field_value, JsonObject):
                final_dict[field_key] = Pykson.to_json(field_value)
            elif isinstance(field_value, list):
                list_value = []
                for item in field_value:
                    if isinstance(item, JsonObject):
                        list_value.append(Pykson.to_json(item))
                    else:
                        list_value.append(item)
                final_dict[field_key] = list_value
            else:
                final_dict[field_key] = field_value
        return json.dumps(final_dict)