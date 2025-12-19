import json
import io
import zipfile
from pathlib import Path
from typing import Dict, List


class StaticTestManager:
    def __init__(self, output_dir_root: str = "./output"):
        self.output_dir_root = output_dir_root

    def __get_static_test_dir(self, id: str) -> str:
        return f"{self.output_dir_root}/{id}"

    def get_list(self) -> List[str]:
        path = Path(self.output_dir_root)
        if not path.is_dir():
            return []

        ids = []

        for entry in path.iterdir():
            if entry.is_dir():
                ids.append(entry.name)

        static_tests = []

        for id in ids:
            result = self.get_by_id(id)
            static_tests.append(
                {
                    "id": result.get("id"),
                    "name": result.get("name"),
                    "created_at": result.get("created_at"),
                }
            )

        return static_tests

    def get_by_id(self, id: str, result_filename: str = "static_test_result.json"):
        dir_path = self.__get_static_test_dir(id)

        if not Path(dir_path).is_dir():
            return None

        file_path = f"{dir_path}/{result_filename}"

        if not Path(file_path).is_file():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def export_by_id(
        self,
        id: str,
        filenames: Dict[str, str] = {
            "static_test_insights.txt": "insights.txt",
            "static_test_result.csv": "result.csv",
            "static_test_result.json": "result.json",
            "thrust_time_chart.png": "chart.png",
        },
    ):
        dir_path = self.__get_static_test_dir(id)

        if not Path(dir_path).is_dir():
            return None

        files_to_zip: Dict[str, str] = {}
        for file_path, arcname in filenames.items():
            file_path = f"{dir_path}/{file_path}"
            if Path(file_path).is_file():
                files_to_zip[file_path] = arcname

        if len(files_to_zip) == 0:
            return None

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_path, arcname in files_to_zip.items():
                zip_file.write(file_path, arcname=arcname)

        zip_buffer.seek(0)

        return zip_buffer
