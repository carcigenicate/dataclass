from unittest import TestCase

from my_dataclass import MyDataclass


class BasicTestCaseBase(TestCase):
    def setUp(self):
        class TestClass(MyDataclass):
            a: int
            b: int

        self.test_class = TestClass
        self.obj1 = self.test_class(12, 34)
        self.obj2 = self.test_class(98, 76)


class BasicClassCreationTestCase(BasicTestCaseBase):
    def test_valid_class_creation(self):
        self.assertEqual(self.test_class.__slots__, ("a", "b"))


class BasicInstanceCreationTestCase(BasicTestCaseBase):
    def test_valid_instance_creation(self):
        self.assertEqual((self.obj1.a, self.obj1.b), (12, 34))

    def test_instances_are_independent(self):
        self.assertEqual((self.obj1.a, self.obj1.b), (12, 34))
        self.assertEqual((self.obj2.a, self.obj2.b), (98, 76))

        self.obj1.a = 19
        self.obj2.b = 28

        self.assertEqual((self.obj1.a, self.obj1.b), (19, 34))
        self.assertEqual((self.obj2.a, self.obj2.b), (98, 28))


class InitializationTestCase(BasicTestCaseBase):
    def test_kwargs(self):
        obj = self.test_class(a=1, b=2)
        self.assertEqual((obj.a, obj.b), (1, 2))

    def test_out_of_order_kwargs(self):
        obj = self.test_class(b=9, a=8)
        self.assertEqual((obj.a, obj.b), (8, 9))

    def test_mixed(self):
        obj = self.test_class(1, b=2)
        self.assertEqual((obj.a, obj.b), (1, 2))

    def test_missing_argument(self):
        with self.assertRaises(TypeError):
            self.test_class()

        with self.assertRaises(TypeError):
            self.test_class(1)

        with self.assertRaises(TypeError):
            self.test_class(a=1)

        with self.assertRaises(TypeError):
            self.test_class(b=2)

    def test_too_many_arguments(self):
        with self.assertRaises(TypeError):
            self.test_class(1, 2, 3)

        with self.assertRaises(TypeError):
            self.test_class(1, a=2, b=3)


class DefaultingInstanceCreationTestCase(TestCase):
    def test_default_last(self):
        class TestClass(MyDataclass):
            a: int
            b: int = 2

        obj = TestClass(1)
        self.assertEqual((obj.a, obj.b), (1, 2))

    def test_default_all(self):
        class TestClass(MyDataclass):
            a: int = 1
            b: int = 2

        obj = TestClass()
        self.assertEqual((obj.a, obj.b), (1, 2))

    def test_illegal_defaults(self):
        with self.assertRaises(TypeError):
            class TestClass(MyDataclass):
                a: int = 1
                b: int

        with self.assertRaises(TypeError):
            class TestClass(MyDataclass):
                a: int
                b: int = 1
                c: int


class BasicAttributeTestCase(BasicTestCaseBase):
    # This functionality actually diverges from the built-in dataclasses.
    def test_attributes_closed(self):
        with self.assertRaises(AttributeError):
            self.obj1.bad_attr = 1


class SpecialMethodTestCase(BasicTestCaseBase):
    def test_str(self):
        self.assertEqual(str(self.obj1), "TestClass(a=1, b=2)")