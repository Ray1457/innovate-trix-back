from fastapi import FastAPI # type: ignore

app = FastAPI(title="Innovate Trix API")


@app.get("/")
def root():
    return {"message": "Innovate Trix API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
