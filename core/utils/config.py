"""Configuration file parser module"""

import json
import os
import shutil

import unittest


class ConfigSet:
    """A class to contain and parse all configuration files"""

    main_config_file_path = os.path.join("configs", "main-config.json")
    api_config_file_path = os.path.join("configs", "api-keys.json")

    def parse_file(self, file_path) -> tuple[dict, bool]:
        """
        Open a json file and parse its contents

        returns (content:dict, existed:bool)

        content = parsed file content | {} if None
        existed = did the file exist before function was ran (true)
        or did the progam generate it (false)
        """

        try:
            file = open(file_path, "r")
            file.close()
            existed = True
        except FileNotFoundError:
            file = open(file_path, "w")
            file.write("")
            file.close()
            existed = False

        try:
            file = open(file_path, "r")
            content = json.load(file)
            file.close()
        except json.JSONDecodeError:
            file = open(file_path, "w")
            json.dump({}, file)
            content = {}
            file.close()

        return content, existed
    

    def get_value(self, file_path:str, value_path:str):
        """
        Check for a value in a json file

        file_path = file to check in
        value_path = a path for the value inside the value
        (example: 'HostingOptions.port')
        """
        
        file_content,_ = self.parse_file(file_path)
        
        value_path = value_path.split(".")

        # Remove all occurances of "."
        value_path=[j for _,j in enumerate(value_path) if j!="."]

        if len(value_path) != 2:
            raise Exception("Value path must be composed of two values only!")


        try:
            return file_content[value_path[0]][value_path[1]]
        except:
            return None


class TestCases(unittest.TestCase):

    """
    Test class for this file
    """

    def test_parse_file(self):
        test_file_path = os.path.join(".test-cache", "test.json")
        class_instance = ConfigSet()

        self.assertEqual(
            class_instance.parse_file(test_file_path),
            ({}, False)
        )

        self.assertEqual(
            class_instance.parse_file(test_file_path),
            ({}, True)
        )

        test_file_path_2 = os.path.join(".test-cache", "test-2.json")

        dump_content = {
            "test": True,
            "test_2":{
                "port":80,
                "interface":"0.0.0.0"
            }
        }

        file = open(test_file_path_2, "w")
        json.dump(dump_content, file, indent=3)
        file.close()

        self.assertEqual(
            class_instance.parse_file(test_file_path_2),
            (dump_content, True)
        )

    def test_get_value(self):
        class_instance = ConfigSet()
        test_file_path_2 = os.path.join(".test-cache", "test-2.json")

        dump_content = {
            "test": True,
            "test_2":{
                "port":80,
                "interface":"0.0.0.0"
            }
        }

        file = open(test_file_path_2, "w")
        json.dump(dump_content, file, indent=3)
        file.close()

        self.assertEqual(
            class_instance.get_value(
                test_file_path_2,
                "test_2.port"
            ),80
        )

        self.assertEqual(
            class_instance.get_value(
                test_file_path_2,
                "test_2.does_not_exist"
            ),None
        )


if __name__ == "__main__":
    try:
        shutil.rmtree(os.path.join(".test-cache"))
    except FileNotFoundError:
        pass

    os.mkdir(os.path.join(".test-cache"))
    
    unittest.main()
