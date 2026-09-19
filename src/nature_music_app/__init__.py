def main() -> None:
    import uvicorn

    uvicorn.run("nature_music_app.api:app", host="127.0.0.1", port=8001)
