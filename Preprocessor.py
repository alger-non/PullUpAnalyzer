import os
from os import walk

try:
    from openpose import pyopenpose as op
except ImportError as e:
    print(
        'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e

# the directory containing video files for preprocessing
queue_dir = '/home/algernon/samba/video_queue/queue'
# the directory in which will be placed source video files
# from the queue_dir together with json files after preprocesing
input_dir = '/home/algernon/samba/video_queue/input'
# the directory containing pretrained models using by OpenPose
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
    # we want to detect key points only for one person(athlete)
    params['number_people_max'] = 1
    # it will print on the command line every `verbose` frames
    params['cli_verbose'] = 100
    # the following two params disable video displaying
    params['render_pose'] = 0
    params['display'] = 0
    # the directory to write OpenPose output in JSON format
    params['write_json'] = os.path.join(output_video_dir, f'{input_video.split(".")[0]}_json')
    # use a video file instead of the camera
    params['video'] = full_input_video_name
    # th folder path (absolute or relative) where the models (pose, face, ...) are located
    params["model_folder"] = models_dir

    try:
        open_pose = op.WrapperPython(3)
        open_pose.configure(params)
        open_pose.execute()
        os.rename(full_input_video_name, os.path.join(output_video_dir, input_video))

    except Exception as e:
        print(e)

print("Preprocessor finished.")
