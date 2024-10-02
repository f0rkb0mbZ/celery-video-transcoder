from celery import shared_task
import ffmpeg
import re
import sys
from celery_worker import app

@app.task(bind=True)
def resize_video(self, input_file: str, output_file: str, height: int, cuda=False):
    if cuda:
        ffmpeg.input(input_file, hwaccel='cuda').output(output_file, vf=f'hwupload_cuda,scale_cuda=w=-1:h={height}',
                                                        vcodec='h264_nvenc').overwrite_output().run()
    else:
        # CPU encoder needs width divisible by 2, otherwise it will fail
        ffmpeg.input(input_file).filter('scale', 'trunc(oh * (iw/ih)/2) * 2', height).output(output_file).overwrite_output().run()


@app.task(bind=True)
def resize_video_with_progress(self, input_file: str, output_file: str, height: int, media_length: int, cuda=False):
    if cuda:
        ff_process = ffmpeg.input(input_file, hwaccel='cuda').output(output_file, vf=f'hwupload_cuda,scale_cuda=w=-1:h={height}',
                                                        vcodec='h264_nvenc').overwrite_output().run_async(pipe_stderr=True, pipe_stdout=True)
    else:
        # CPU encoder needs width divisible by 2, otherwise it will fail
        ff_process = ffmpeg.input(input_file).filter('scale', 'trunc(oh * (iw/ih)/2) * 2', height).output(output_file).overwrite_output().run_async(pipe_stderr=True, pipe_stdout=True)

    # Regex to extract time progress (time=00:00:03.00)
    time_re = re.compile(r'time=(\d+:\d+:\d+\.\d+)')

    # FFmpeg doesn't print new lines, it overwrites the same line.
    # We'll read continuously from stderr
    progress = ''

    def time_to_seconds(time_str):
        hours, minutes, seconds = map(float, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds

    while True:
        # Read 1024 bytes from stderr (ffmpeg output comes here)
        chunk = ff_process.stderr.read(1024).decode('utf-8')

        if not chunk:
            break

        progress += chunk

        # Look for 'time' updates in the progress stream
        time_match = time_re.findall(progress)
        if time_match:
            elapsed_time = time_match[-1]  # Get the last captured time
            percent_complete = int((time_to_seconds(elapsed_time) / media_length) * 100)
            print(f"Progress for {output_file}: {percent_complete}")
            self.update_state(state='PROGRESS', meta={'progress': percent_complete})
            sys.stdout.flush()  # Ensure the progress is printed immediately

        # Optionally, clear the buffer to avoid excess memory usage
        progress = progress[-1000:]  # Keep only the last 1000 characters

    ff_process.wait()

    if ff_process.returncode == 0:
        print("FFmpeg process completed successfully.")
    else:
        print(f"FFmpeg process failed with return code {ff_process.returncode}.")
