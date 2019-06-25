import os
from os import walk
import sys

try:
    from openpose import pyopenpose as op
except ImportError as e:
    print(
        'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e

queue_dir = '/home/algernon/samba/video_queue/queue'
input_dir = '/home/algernon/samba/video_queue/input'
models_dir = 'models'

input_videos = []
for _, _, f_names in walk(queue_dir):
    input_videos.extend(f_names)
    break

for input_video in input_videos:
    full_input_video_name = os.path.join(queue_dir, input_video)
    output_video_dir = os.path.join(input_dir, input_video.split('.')[0])
    try:
        os.mkdir(output_video_dir)
    except OSError:
        print(f"Creation of the directory {output_video_dir} failed")

    params = dict()
    params['number_people_max'] = 1
    params['cli_verbose'] = 100
    # next two params disable video displaying
    params['render_pose'] = 0
    params['display'] = 0
    params['write_json'] = os.path.join(output_video_dir, f'{input_video.split(".")[0]}_json')
    params['video'] = full_input_video_name
    params["model_folder"] = models_dir

    try:
        open_pose = op.WrapperPython(3)
        open_pose.configure(params)
        open_pose.execute()
    except Exception as e:
        print(e)
        sys.exit(-1)
    os.rename(full_input_video_name, os.path.join(output_video_dir, input_video))

print("Preprocessor successfully finished.")
