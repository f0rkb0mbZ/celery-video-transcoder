import os
import random

import ffmpeg
from celery.result import AsyncResult
from fastapi import FastAPI, File, UploadFile
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from helpers.video import resize_video_with_progress

UPLOAD_DIR = "uploads"
STATIC_DIR = "static"
app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "image_url": None, "tasks": None})


@app.post("/upload_file/")
async def upload_handler(request: Request, file: UploadFile = File(...)):
    if request.method == "GET":
        RedirectResponse("/", status_code=307)
    elif request.method == "POST":
        # Read file
        file_contents = await file.read()

        # Allow only video files
        if file.content_type in ['video/mp4', 'video/x-msvideo', 'video/mpeg', 'video/ogg', 'video/webm',
                                 'video/quicktime', 'video/x-matroska']:
            # Create file path
            file_path = os.path.join(UPLOAD_DIR, file.filename)

            # Write file to upload dir
            with open(file_path, "wb") as f:
                f.write(file_contents)

            # Probe the file to get mediainfo
            mediainfo = ffmpeg.probe(file_path)

            # Get length of the media
            media_length = mediainfo.get("format").get("duration")
            thumbnail_path = os.path.join(STATIC_DIR, f"{os.path.splitext(file.filename)[0]}_thumbnail.jpg")

            # Extract thumbnail from a random timestamp
            ffmpeg.input(file_path, ss=random.randint(0, int(float(media_length)))).filter('scale', 1280, -1).output(
                thumbnail_path, vframes=1).overwrite_output().run()

            # Available video heights
            video_heights = [2160, 1440, 1080, 720, 480, 360, 240, 144]

            # Get video stream metadata from the 1st stream
            video_metadata = None
            for stream in mediainfo.get("streams"):
                if stream.get("codec_type") == "video":
                    video_metadata = stream

            # Extract video height
            video_height = video_metadata.get("height")
            print(f'Video height is: {video_height}')

            # Store the task ids in a dict
            tasks = dict()
            for height in video_heights:
                if video_height > height:
                    # Downscale to all lower resolutions
                    print(f'Queueing video to downscale to {height}p!')
                    output_file = f"{os.path.splitext(file.filename)[0]}_{height}p.mp4"
                    tasks[f'{height}p'] = {'file': output_file,
                                           'task': resize_video_with_progress.delay(input_file=file_path,
                                                                                    output_file=os.path.join(STATIC_DIR,
                                                                                                             output_file),
                                                                                    height=height,
                                                                                    media_length=int(
                                                                                        float(media_length)),
                                                                                    cuda=False)}

            return templates.TemplateResponse("index.html",
                                              {"request": request, "image_url": f"/{thumbnail_path}", "tasks": tasks})
        else:
            return templates.TemplateResponse("index.html", {"request": request, "image_url": None,
                                                             "error": "Only video files are supported!"})


@app.get("/task_status/{task_id}/")
async def get_transcoding_status(request: Request, task_id: str):
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        return {'state': task.state, 'progress': 0}
    elif task.state == 'FAILURE':
        return {'state': task.state, 'progress': -1}
    elif task.state == 'SUCCESS':
        return {'state': task.state, 'progress': 100}
    elif task.state == 'PROGRESS':
        return {'state': task.state, 'progress': task.info.get('progress', 0)}
    else:
        return {'state': task.state, 'progress': 0}
