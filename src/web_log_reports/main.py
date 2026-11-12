"""Minimal API prototype; storage is limited to the current process."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from web_log_reports.analytics import summarize
from web_log_reports.parser import LogRecord, parse_line


class LogBatch(BaseModel):
    lines: list[str] = Field(min_length=1, max_length=1000)


def create_app() -> FastAPI:
    application = FastAPI(title="Web Log Reports", version="0.1.0")
    records: list[LogRecord] = []

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post("/logs", status_code=201)
    def ingest(batch: LogBatch) -> dict[str, int]:
        try:
            parsed = [parse_line(line) for line in batch.lines]
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        records.extend(parsed)
        return {"accepted": len(parsed)}

    @application.get("/stats")
    def stats() -> dict[str, int | float]:
        return summarize(records)

    return application


app = create_app()
