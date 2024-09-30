from celery import shared_task
import ffmpeg


@shared_task(bind=True)
def resize_video(self, input_file: str, output_file: str, height: int, cuda=False):
    if cuda:
        ffmpeg.input(input_file, hwaccel='cuda').output(output_file, vf=f'hwupload_cuda,scale_cuda=w=-1:h={height}',
                                                        vcodec='h264_nvenc').overwrite_output().run()
    else:
        # CPU encoder needs width divisible by 2, otherwise it will fail
        ffmpeg.input(input_file).filter('scale', 'trunc(oh * (iw/ih)/2) * 2', height).output(output_file).overwrite_output().run()
