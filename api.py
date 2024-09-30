from fastapi import FastAPI, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
import os
import shutil
import ffmpeg
import random

from helpers.video import resize_video

UPLOAD_DIR = "uploads"
STATIC_DIR = "static"
app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "image_url": None})


@app.post("/uploadfile/")
async def upload_handler(request: Request, file: UploadFile = File(...)):
    if request.method == "GET":
        RedirectResponse("/", status_code=307)
    elif request.method == "POST":
        # Read file
        file_contents = await file.read()
        if file.content_type in ['video/mp4']:
            # Create file path
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            # Write file to upload dir
            with open(file_path, "wb") as f:
                f.write(file_contents)
            # Probe the file to get mediainfo
            mediainfo = ffmpeg.probe(file_path)
            # Get length of the media
            media_length = mediainfo.get("format").get("duration")
            thumbnail_path = os.path.join(STATIC_DIR, f"{file.filename}_thumbnail.jpg")
            # Extract thumbnail from a random timestamp
            ffmpeg.input(file_path, ss=random.randint(0, int(float(media_length)))).filter('scale', 1280, -1).output(
                thumbnail_path, vframes=1).overwrite_output().run()
            resize_video.delay(input_file=file_path, output_file=os.path.join(STATIC_DIR, f"{file.filename}_720p.mp4"),
                               width=720, cuda=True)
            return templates.TemplateResponse("index.html", {"request": request, "image_url": f"/{thumbnail_path}"})
        else:
            return templates.TemplateResponse("index.html", {"request": request, "image_url": None,
                                                             "error": "Only video files are supported!"})


d = {'streams': [{'index': 0,
                  'codec_name': 'h264',
                  'codec_long_name': 'H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10',
                  'profile': 'High',
                  'codec_type': 'video',
                  'codec_tag_string': 'avc1',
                  'codec_tag': '0x31637661',
                  'width': 1920,
                  'height': 1080,
                  'coded_width': 1920,
                  'coded_height': 1080,
                  'closed_captions': 0,
                  'film_grain': 0,
                  'has_b_frames': 0,
                  'sample_aspect_ratio': '1:1',
                  'display_aspect_ratio': '16:9',
                  'pix_fmt': 'yuv420p',
                  'level': 42,
                  'chroma_location': 'left',
                  'field_order': 'progressive',
                  'refs': 1,
                  'is_avc': 'true',
                  'nal_length_size': '4',
                  'id': '0x1',
                  'r_frame_rate': '25/1',
                  'avg_frame_rate': '25/1',
                  'time_base': '1/25000',
                  'start_pts': 0,
                  'start_time': '0.000000',
                  'duration_ts': 30899000,
                  'duration': '1235.960000',
                  'bit_rate': '20976545',
                  'bits_per_raw_sample': '8',
                  'nb_frames': '30899',
                  'extradata_size': 41,
                  'disposition': {'default': 1,
                                  'dub': 0,
                                  'original': 0,
                                  'comment': 0,
                                  'lyrics': 0,
                                  'karaoke': 0,
                                  'forced': 0,
                                  'hearing_impaired': 0,
                                  'visual_impaired': 0,
                                  'clean_effects': 0,
                                  'attached_pic': 0,
                                  'timed_thumbnails': 0,
                                  'non_diegetic': 0,
                                  'captions': 0,
                                  'descriptions': 0,
                                  'metadata': 0,
                                  'dependent': 0,
                                  'still_image': 0},
                  'tags': {'creation_time': '2022-11-07T17:06:40.000000Z',
                           'language': 'eng',
                           'handler_name': '\x1fMainconcept Video Media Handler',
                           'vendor_id': '[0][0][0][0]',
                           'encoder': 'AVC Coding'}},
                 {'index': 1,
                  'codec_name': 'aac',
                  'codec_long_name': 'AAC (Advanced Audio Coding)',
                  'profile': 'LC',
                  'codec_type': 'audio',
                  'codec_tag_string': 'mp4a',
                  'codec_tag': '0x6134706d',
                  'sample_fmt': 'fltp',
                  'sample_rate': '48000',
                  'channels': 2,
                  'channel_layout': 'stereo',
                  'bits_per_sample': 0,
                  'initial_padding': 0,
                  'id': '0x2',
                  'r_frame_rate': '0/0',
                  'avg_frame_rate': '0/0',
                  'time_base': '1/48000',
                  'start_pts': 0,
                  'start_time': '0.000000',
                  'duration_ts': 59326080,
                  'duration': '1235.960000',
                  'bit_rate': '317370',
                  'nb_frames': '57937',
                  'extradata_size': 2,
                  'disposition': {'default': 1,
                                  'dub': 0,
                                  'original': 0,
                                  'comment': 0,
                                  'lyrics': 0,
                                  'karaoke': 0,
                                  'forced': 0,
                                  'hearing_impaired': 0,
                                  'visual_impaired': 0,
                                  'clean_effects': 0,
                                  'attached_pic': 0,
                                  'timed_thumbnails': 0,
                                  'non_diegetic': 0,
                                  'captions': 0,
                                  'descriptions': 0,
                                  'metadata': 0,
                                  'dependent': 0,
                                  'still_image': 0},
                  'tags': {'creation_time': '2022-11-07T17:06:40.000000Z',
                           'language': 'eng',
                           'handler_name': '#Mainconcept MP4 Sound Media Handler',
                           'vendor_id': '[0][0][0][0]'}}],
     'format': {'filename': 'forcasting.mp4',
                'nb_streams': 2,
                'nb_programs': 0,
                'format_name': 'mov,mp4,m4a,3gp,3g2,mj2',
                'format_long_name': 'QuickTime / MOV',
                'start_time': '0.000000',
                'duration': '1235.960000',
                'size': '3290249945',
                'bit_rate': '21296805',
                'probe_score': 100,
                'tags': {'major_brand': 'mp42',
                         'minor_version': '0',
                         'compatible_brands': 'mp42mp41',
                         'creation_time': '2022-11-07T17:06:40.000000Z'}}}
