from enum import Enum
from typing import List
from unittest.case import TestCase
import datetime
import jsons
import json
from jsons import JsonSerializable
from jsons._common_impl import snakecase, camelcase, pascalcase, lispcase


class TestJsons(TestCase):

    def test_dump_str(self):
        self.assertEqual('some string', jsons.dump('some string'))

    def test_dump_int(self):
        self.assertEqual(123, jsons.dump(123))

    def test_dump_float(self):
        self.assertEqual(123.456, jsons.dump(123.456))

    def test_dump_bool(self):
        self.assertEqual(True, jsons.dump(True))

    def test_dump_dict(self):
        self.assertEqual({'a': 123}, jsons.dump({'a': 123}))

    def test_dump_none(self):
        self.assertEqual(None, jsons.dump(None))

    def test_dump_datetime(self):
        d = datetime.datetime(year=2018, month=7, day=8, hour=21, minute=34)
        self.assertEqual('2018-07-08T21:34:00Z', jsons.dump(d))

    def test_dump_datetime_with_microseconds(self):
        d = datetime.datetime(year=2018, month=7, day=8, hour=21, minute=34,
                              microsecond=123456)
        self.assertEqual('2018-07-08T21:34:00.123456Z', jsons.dump(d))

    def test_dump_enum(self):
        class E(Enum):
            x = 1
            y = 2
        self.assertEqual('x', jsons.dump(E.x))

    def test_dump_list(self):
        d = datetime.datetime(year=2018, month=7, day=8, hour=21, minute=34)
        l = [1, 2, 3, [4, 5, [d]]]
        self.assertEqual([1, 2, 3, [4, 5, ['2018-07-08T21:34:00Z']]],
                         jsons.dump(l))

    def test_dump_object(self):
        class A:
            def __init__(self):
                self.name = 'A'

        class B:
            def __init__(self, a):
                self.a = a
                self.name = 'B'

        b = B(A())
        self.assertEqual({'name': 'B', 'a': {'name': 'A'}}, jsons.dump(b))

    def test_load_str(self):
        self.assertEqual('some string', jsons.load('some string'))

    def test_load_int(self):
        self.assertEqual(123, jsons.load(123))

    def test_load_float(self):
        self.assertEqual(123.456, jsons.load(123.456))

    def test_load_bool(self):
        self.assertEqual(True, jsons.load(True))

    def test_load_dict(self):
        self.assertEqual({'a': 123}, jsons.load({'a': 123}))

    def test_load_none(self):
        self.assertEqual(None, jsons.load(None))

    def test_load_datetime(self):
        d = datetime.datetime(year=2018, month=7, day=8, hour=21, minute=34)
        self.assertEqual(d, jsons.load('2018-07-08T21:34:00Z'))

    def test_load_enum(self):
        class E(Enum):
            x = 1
            y = 2

        self.assertEqual(E.x, jsons.load('x', E))

    def test_load_list(self):
        d = datetime.datetime(year=2018, month=7, day=8, hour=21, minute=34)
        l = [1, 2, 3, [4, 5, [d]]]
        expectation = [1, 2, 3, [4, 5, ['2018-07-08T21:34:00Z']]]
        self.assertEqual(l, jsons.load(expectation))

    def test_load_object(self):
        class A:
            def __init__(self):
                self.name = 'A'

        class B:
            def __init__(self, a: A):
                self.a = a
                self.name = 'B'

        b = B(A())
        loaded_b = jsons.load({'name': 'B', 'a': {'name': 'A'}}, B)
        self.assertEqual(b.name, loaded_b.name)
        self.assertEqual(b.a.name, loaded_b.a.name)

    def test_load_object_with_default_value(self):
        class A:
            def __init__(self, x, y = 2):
                self.x = x
                self.y = y

        a = A(1)
        loaded_a = jsons.load({'x': 1}, A)
        self.assertEqual(a.x, loaded_a.x)
        self.assertEqual(a.y, loaded_a.y)

    def test_dump_load_object_deep(self):
        class A:
            def __init__(self):
                self.name = 'A'

        class B:
            def __init__(self, list_a: List[A],
                         list_dates: List[datetime.datetime]):
                self.list_a = list_a
                self.list_dates = list_dates
                self.name = 'B'

        class C:
            def __init__(self, list_b: List[B]):
                self.list_b = list_b

        c = C([B([A(), A()], []),
               B([], [datetime.datetime.now(), datetime.datetime.now()])])
        dumped_c = jsons.dump(c)
        loaded_c = jsons.load(dumped_c, C)
        self.assertEqual(loaded_c.list_b[0].name, 'B')
        self.assertEqual(loaded_c.list_b[0].list_a[0].name, 'A')
        self.assertEqual(loaded_c.list_b[0].list_a[1].name, 'A')
        self.assertEqual(loaded_c.list_b[1].list_dates[0].year,
                         c.list_b[1].list_dates[0].year)
        self.assertEqual(loaded_c.list_b[1].list_dates[0].month,
                         c.list_b[1].list_dates[0].month)
        self.assertEqual(loaded_c.list_b[1].list_dates[0].day,
                         c.list_b[1].list_dates[0].day)
        self.assertEqual(loaded_c.list_b[1].list_dates[0].hour,
                         c.list_b[1].list_dates[0].hour)
        self.assertEqual(loaded_c.list_b[1].list_dates[0].minute,
                         c.list_b[1].list_dates[0].minute)
        self.assertEqual(loaded_c.list_b[1].list_dates[0].second,
                         c.list_b[1].list_dates[0].second)

    def test_dumps(self):
        class A:
            def __init__(self):
                self.name = 'A'

        class B:
            def __init__(self, a: A):
                self.a = a
                self.name = 'B'

        sdumped = jsons.dumps(B(A()))
        s = json.dumps({'a': {'name': 'A'}, 'name': 'B'})
        self.assertEqual(s, sdumped)

    def test_loads(self):
        class A:
            def __init__(self):
                self.name = 'A'

        class B:
            def __init__(self, a: A):
                self.a = a
                self.name = 'B'

        s = json.dumps({'a': {'name': 'A'}, 'name': 'B'})
        loaded_dict = jsons.loads(s)
        self.assertEqual('B', loaded_dict['name'])
        self.assertEqual('A', loaded_dict['a']['name'])

        loaded_obj = jsons.loads(s, B)
        self.assertEqual('B', loaded_obj.name)
        self.assertEqual('A', loaded_obj.a.name)

    def test_jsonserializable(self):
        class Person(JsonSerializable):
            def __init__(self, name, age):
                self.name = name
                self.age = age

        person = Person('John', 65)
        person_json = person.json
        person_loaded = Person.from_json(person_json)

        self.assertEqual(person_json, {'name': 'John', 'age': 65})
        self.assertEqual(person_loaded.name, 'John')
        self.assertEqual(person_loaded.age, 65)

    def test_case_transformers(self):
        camelcase_str = 'camelCase'
        snakecase_str = 'snake_case'
        pascalcase_str = 'Pascal_case'
        pascalcase_str2 = 'ABcDe'
        lispcase_str = 'lisp-case'

        self.assertEqual(camelcase(camelcase_str), 'camelCase')
        self.assertEqual(camelcase(snakecase_str), 'snakeCase')
        self.assertEqual(camelcase(pascalcase_str), 'pascalCase')
        self.assertEqual(camelcase(pascalcase_str2), 'aBcDe')
        self.assertEqual(camelcase(lispcase_str), 'lispCase')

        self.assertEqual(snakecase(camelcase_str), 'camel_case')
        self.assertEqual(snakecase(snakecase_str), 'snake_case')
        self.assertEqual(snakecase(pascalcase_str), 'pascal_case')
        self.assertEqual(snakecase(pascalcase_str2), 'a_bc_de')
        self.assertEqual(snakecase(lispcase_str), 'lisp_case')

        self.assertEqual(pascalcase(camelcase_str), 'CamelCase')
        self.assertEqual(pascalcase(snakecase_str), 'SnakeCase')
        self.assertEqual(pascalcase(pascalcase_str), 'PascalCase')
        self.assertEqual(pascalcase(pascalcase_str2), 'ABcDe')
        self.assertEqual(pascalcase(lispcase_str), 'LispCase')

        self.assertEqual(lispcase(camelcase_str), 'camel-case')
        self.assertEqual(lispcase(snakecase_str), 'snake-case')
        self.assertEqual(lispcase(pascalcase_str), 'pascal-case')
        self.assertEqual(lispcase(pascalcase_str2), 'a-bc-de')
        self.assertEqual(lispcase(lispcase_str), 'lisp-case')

    def test_serialize_and_deserialize_with_case_transformer(self):
        class A:
            def __init__(self, snake_case_str):
                self.snake_case_str = snake_case_str

        class B:
            def __init__(self, a_obj: A, camel_case_str):
                self.a_obj = a_obj
                self.camel_case_str = camel_case_str

        b = B(A('one_two'), 'theeFour')
        dumped_pascalcase = \
            jsons.dump(b, key_transformer=jsons.KEY_TRANSFORMER_PASCALCASE)
        loaded_snakecase = \
            jsons.load(dumped_pascalcase, B,
                       key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE)
        expected_dump = {'AObj': {'SnakeCaseStr': 'one_two'},
                    'CamelCaseStr': 'theeFour'}
        self.assertEqual(expected_dump, dumped_pascalcase)
        self.assertEqual(loaded_snakecase.a_obj.snake_case_str, 'one_two')
        self.assertEqual(loaded_snakecase.camel_case_str, 'theeFour')
