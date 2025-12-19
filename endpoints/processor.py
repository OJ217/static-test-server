import os
import uuid
import csv
import json
from datetime import datetime
from typing import List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


class StaticTestProcessor:
    # Init
    def __init__(
        self,
        raw_data: List[float],
        name: str,
        total_mass_loss: float,
        time_interval: float,
        output_dir_root: str = "./output",
    ):
        self.name = name
        self.id = uuid.uuid4()
        self.output_dir = f"{output_dir_root}/{self.id}"

        print(self.name, self.id, self.output_dir)

        self.raw_data = raw_data
        self.total_mass_loss = total_mass_loss
        self.time_interval = time_interval
        self.__processed = False
        self.__g = 9.80665

        self.time_frame: List[float] = []
        self.mass: List[float] = []
        self.mass_loss: List[float] = []
        self.raw_mass: List[float] = []
        self.force: List[float] = []
        self.impulse: List[float] = []

        self.total_impulse: float = 0.0
        self.force_max: float = 0.0
        self.duration: float = 0.0

        self.aggregated_result: any = None

    # Processor and aggregator
    def process(self) -> None:
        sample_count = len(self.raw_data)
        self.time_frame = [i * self.time_interval for i in range(sample_count)]
        self.duration = self.time_frame[-1] if self.time_frame else 0

        self.mass = [0]
        for i in range(1, sample_count):
            self.mass.append(self.raw_data[i] - self.raw_data[i - 1] + self.mass[i - 1])

        if self.duration == 0:
            avg_mass_loss = 0
        else:
            avg_mass_loss = self.total_mass_loss / self.duration
        self.mass_loss = [i * avg_mass_loss for i in self.time_frame]

        self.raw_mass = [x + y for x, y in zip(self.mass, self.mass_loss)]

        # Calculate force and impulse
        self.force = [(m / 1000) * self.__g for m in self.raw_mass]
        self.impulse = [f * self.time_interval for f in self.force]

        # Calculate insights
        self.total_impulse = sum(self.impulse)
        self.force_max = max(self.force) if self.force else 0

        self.__processed = True
        self.save()

    def __aggregate_result(self):
        if not self.__processed:
            self.process()

        result = [
            {
                "time": row[0],
                "mass": row[1],
                "raw_mass": row[2],
                "mass_loss": row[3],
                "force": row[4],
                "impulse": row[5],
            }
            for row in zip(
                self.time_frame,
                self.mass,
                self.raw_mass,
                self.mass_loss,
                self.force,
                self.impulse,
            )
        ]

        insights = {
            "total_impulse": self.total_impulse,
            "force_max": self.force_max,
            "duration": self.duration,
        }

        self.aggregated_result = {
            "id": str(self.id),
            "name": self.name,
            "time_interval": self.time_interval,
            "total_mass_loss": self.total_mass_loss,
            "input": self.raw_data,
            "result": result,
            "insights": insights,
            "created_at": datetime.now().isoformat(),
        }

    def get_aggregated_result(self) -> any:
        if self.aggregated_result is None:
            self.__aggregate_result()

        return self.aggregated_result

    # File management
    def __build_file_path(self, filename: str) -> str:
        file_path = f"{self.output_dir}/{filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return file_path

    def __save_chart(
        self,
        filename: str = "thrust_time_chart.png",
    ) -> None:
        plt.plot(self.time_frame, self.force)
        plt.xlabel("Time (s)")
        plt.ylabel("Thrust (N)")
        plt.title("Thrust vs Time")

        file_path = self.__build_file_path(filename)
        plt.savefig(file_path)

        plt.close()

    def __save_csv(
        self,
        filename: str = "static_test_result.csv",
    ) -> None:
        headers = [
            "Time (s)",
            "Mass (g)",
            "Raw mass (g)",
            "Mass loss (g)",
            "Force (N)",
            "Impulse (N*s)",
        ]
        rows = zip(
            self.time_frame,
            self.mass,
            self.raw_mass,
            self.mass_loss,
            self.force,
            self.impulse,
        )

        file_path = self.__build_file_path(filename)
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)

    def __save_insights(
        self,
        filename: str = "static_test_insights.txt",
    ) -> None:
        insights = (
            f"Static test insights:\n"
            f"total impulse  (N*s)    - {self.total_impulse:.2f}\n"
            f"force max      (N)      - {self.force_max:.2f}\n"
            f"total duration (s)      - {self.duration:.2f}"
        )

        file_path = self.__build_file_path(filename)
        with open(file_path, mode="w") as file:
            file.write(insights)

    def __save_json(
        self,
        filename: str = "static_test_result.json",
    ) -> None:
        if self.aggregated_result is None:
            self.__aggregate_result()

        file_path = self.__build_file_path(filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.aggregated_result, f, ensure_ascii=False, indent=4)

    def save(self) -> None:
        if not self.__processed:
            self.process()

        self.__save_chart()
        self.__save_csv()
        self.__save_insights()
        self.__save_json()
