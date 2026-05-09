from dataclasses import dataclass

from flask import Response


@dataclass(frozen=True)
class CsvDownload:
    filename: str
    content: str


def build_csv_response(download: CsvDownload) -> Response:
    return Response(
        download.content,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={download.filename}"
        },
    )


def build_training_export_download(csv_content: str) -> CsvDownload:
    return CsvDownload(
        filename="training_data_export.csv",
        content=csv_content,
    )


def build_prediction_governance_export_download(csv_content: str) -> CsvDownload:
    return CsvDownload(
        filename="prediction_governance_export.csv",
        content=csv_content,
    )
