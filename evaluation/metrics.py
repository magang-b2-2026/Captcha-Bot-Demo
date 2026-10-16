import csv
import os
from datetime import datetime


class MetricsLogger:
    def __init__(self, output_path="outputs/logs/results.csv"):
        self.output_path = output_path

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

        if not os.path.exists(output_path):
            self._create_file()

    def _create_file(self):
        with open(
            self.output_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "timestamp",
                "url",
                "captcha_type",
                "ocr_result",
                "answer",
                "result",
                "processing_time_seconds"
            ])

    def log(
        self,
        url,
        captcha_type,
        ocr_result,
        answer,
        result,
        processing_time
    ):
        with open(
            self.output_path,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                datetime.now().isoformat(
                    timespec="seconds"
                ),
                url,
                captcha_type,
                ocr_result,
                answer,
                result,
                round(processing_time, 3)
            ])