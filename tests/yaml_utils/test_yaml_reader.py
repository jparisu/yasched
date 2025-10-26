import unittest

from yasched.yaml_utils.exceptions import YamlFormatError, YamlKeyError, YamlTypeError
from yasched.yaml_utils.YamlReader import YamlKey, YamlReader


class TestYamlKey(unittest.TestCase):
    def test_init(self):
        key = YamlKey({"name", "title", "label"})
        self.assertEqual(key.keys, {"name", "title", "label"})

    def test_repr(self):
        key = YamlKey({"name", "title"})
        self.assertIn("YamlKey", repr(key))
        self.assertIn("name", repr(key))


class TestYamlReader(unittest.TestCase):
    # ---------- Construction ----------

    def test_init_valid_yaml(self):
        yaml_str = "name: John\nage: 30"
        reader = YamlReader(yaml_str)
        self.assertIsNotNone(reader._yaml)

    def test_init_empty_yaml(self):
        reader = YamlReader("")
        self.assertEqual(reader._yaml, {})

    def test_init_invalid_yaml_raises(self):
        with self.assertRaises(YamlFormatError):
            YamlReader("invalid: yaml: content: [")

    def test_from_dict(self):
        data = {"name": "John", "age": 30}
        reader = YamlReader.from_dict(data)
        self.assertEqual(reader._yaml, data)

    # ---------- yaml() method ----------

    def test_yaml_method(self):
        reader = YamlReader("")
        reader.yaml({"key": "value"})
        self.assertEqual(reader._yaml, {"key": "value"})

    # ---------- has() method ----------

    def test_has_key_exists(self):
        reader = YamlReader("name: John")
        self.assertTrue(reader.has(YamlKey({"name"})))

    def test_has_key_missing(self):
        reader = YamlReader("name: John")
        self.assertFalse(reader.has(YamlKey({"missing"})))

    def test_has_alternative_keys(self):
        reader = YamlReader("title: Mr. Smith")
        # Should find 'title' even though we also specified 'name'
        self.assertTrue(reader.has(YamlKey({"name", "title"})))

    def test_has_non_dict_yaml(self):
        reader = YamlReader("- item1\n- item2")
        self.assertFalse(reader.has(YamlKey({"key"})))

    # ---------- get() method ----------

    def test_get_existing_key(self):
        reader = YamlReader("name: John\nage: 30")
        self.assertEqual(reader.get(YamlKey({"name"})), "John")
        self.assertEqual(reader.get(YamlKey({"age"})), 30)

    def test_get_alternative_key(self):
        reader = YamlReader("title: Mr. Smith")
        # Should find 'title' when looking for name/title
        self.assertEqual(reader.get(YamlKey({"name", "title"})), "Mr. Smith")

    def test_get_missing_key_with_default(self):
        reader = YamlReader("name: John")
        self.assertEqual(reader.get(YamlKey({"missing"}), default="N/A"), "N/A")

    def test_get_missing_key_throw_false(self):
        reader = YamlReader("name: John")
        self.assertIsNone(reader.get(YamlKey({"missing"}), throw=False))

    def test_get_missing_key_throw_true_raises(self):
        reader = YamlReader("name: John")
        with self.assertRaises(YamlKeyError):
            reader.get(YamlKey({"missing"}))

    def test_get_with_type_validation_valid(self):
        reader = YamlReader("name: John\nage: 30")
        self.assertEqual(reader.get(YamlKey({"name"}), force_type=[str]), "John")
        self.assertEqual(reader.get(YamlKey({"age"}), force_type=[int]), 30)

    def test_get_with_type_validation_invalid_raises(self):
        reader = YamlReader("name: John")
        with self.assertRaises(YamlTypeError):
            reader.get(YamlKey({"name"}), force_type=[int])

    def test_get_with_multiple_valid_types(self):
        reader = YamlReader("value: 42")
        # Should accept int since it's one of the allowed types
        self.assertEqual(reader.get(YamlKey({"value"}), force_type=[str, int]), 42)

    def test_get_non_dict_yaml_raises(self):
        reader = YamlReader("- item1\n- item2")
        with self.assertRaises(YamlKeyError):
            reader.get(YamlKey({"key"}))

    # ---------- get_child() method ----------

    def test_get_child_existing(self):
        reader = YamlReader("person:\n  name: John\n  age: 30")
        child = reader.get_child(YamlKey({"person"}))
        self.assertIsInstance(child, YamlReader)
        self.assertEqual(child.get(YamlKey({"name"})), "John")

    def test_get_child_missing_with_default(self):
        reader = YamlReader("name: John")
        child = reader.get_child(YamlKey({"missing"}), default={}, throw=False)
        self.assertIsInstance(child, YamlReader)
        # Should be empty
        self.assertFalse(child.has(YamlKey({"anything"})))

    def test_get_child_missing_throw_true_raises(self):
        reader = YamlReader("name: John")
        with self.assertRaises(YamlKeyError):
            reader.get_child(YamlKey({"missing"}))

    def test_get_child_non_dict_value(self):
        reader = YamlReader("value: 42")
        child = reader.get_child(YamlKey({"value"}), throw=False)
        # Should return empty YamlReader if value is not a dict
        self.assertIsInstance(child, YamlReader)

    # ---------- dump() method ----------

    def test_dump(self):
        yaml_str = "name: John\nage: 30\n"
        reader = YamlReader(yaml_str)
        dumped = reader.dump()
        self.assertIsInstance(dumped, str)
        self.assertIn("name", dumped)
        self.assertIn("John", dumped)

    def test_dump_empty(self):
        reader = YamlReader("")
        dumped = reader.dump()
        self.assertIsInstance(dumped, str)

    # ---------- repr ----------

    def test_repr(self):
        reader = YamlReader("name: John")
        self.assertIn("YamlReader", repr(reader))


if __name__ == "__main__":
    unittest.main()
