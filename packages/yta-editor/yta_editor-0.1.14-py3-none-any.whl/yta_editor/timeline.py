"""
The timeline module that is the core
of this video editor. A group of 
tracks that include media items to
be played along the time.

A recommendation about formats to 
export:
- 'yuv420p': A final video without alpha
(to upload to Youtube or use in any
video player)
- 'yuva420p': A final video with alpha 
(to create overlays or assets we will
use in other videos)
- 'rgba': To process in memory with
alpha (numpy, OpenGL, PIL)
"""
from yta_editor.track.audio import AudioTrack
from yta_editor.track.video import VideoTrack
from yta_editor.media.video import VideoFileMedia, VideoImageMedia, VideoColorMedia
from yta_editor.utils.frame_wrapper import AudioFrameWrapped
from yta_editor.utils.frame_combinator import AudioFrameCombinator
from yta_editor.utils import VideoUtils
from yta_video_pyav.settings import Settings
from yta_video_pyav.writer import VideoWriter
from yta_video_frame_time.t_fraction import get_ts, fps_to_time_base, T
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from quicktions import Fraction
from functools import reduce
from typing import Union

import numpy as np


# TODO: Maybe singleton (?)
class Timeline:
    """
    Class to represent all the tracks that
    exist on the project and to handle the
    combination of all their frames.
    """

    @property
    def end(
        self
    ) -> Fraction:
        """
        The end of the last video of the track
        that lasts longer. This is the last time
        moment that has to be rendered.
        """
        return max(
            track.end
            for track in self.tracks
        )
    
    @property
    def tracks(
        self
    ) -> list[Union['AudioTrack', 'VideoTrack']]:
        """
        All the tracks we have but ordered by 
        their indexes, from lower index (highest
        priority) to highest index (lowest
        priority).
        """
        return sorted(self._tracks, key = lambda track: track.index)
    
    @property
    def video_tracks(
        self
    ) -> list['VideoTrack']:
        """
        All the video tracks we have but ordered
        by their indexes, from lower index
        (highest priority) to highest index
        (lowest priority).
        """
        return [
            track
            for track in self.tracks
            if PythonValidator.is_instance_of(track, 'VideoTrack')
        ]
    
    @property
    def audio_tracks(
        self
    ) -> list['AudioTrack']:
        """
        All the audio tracks we have but ordered
        by their indexes, from lower index
        (highest priority) to highest index
        (lowest priority).
        """
        return [
            track
            for track in self.tracks
            if PythonValidator.is_instance_of(track, 'AudioTrack')
        ]
    
    @property
    def number_of_tracks(
        self
    ) -> int:
        """
        The number of tracks we have in the
        timeline.
        """
        return len(self.tracks)

    @property
    def number_of_video_tracks(
        self
    ) -> int:
        """
        The number of video tracks we have in the
        timeline.
        """
        return len(self.video_tracks)
    
    @property
    def number_of_audio_tracks(
        self
    ) -> int:
        """
        The number of audio tracks we have in the
        timeline.
        """
        return len(self.audio_tracks)

    def __init__(
        self,
        size: tuple[int, int] = Settings.DEFAULT_VIDEO_SIZE.value, # (1920, 1080) before
        fps: Union[int, float, Fraction] = Settings.DEFAULT_VIDEO_FPS.value, # 60.0 before
        audio_fps: Union[int, Fraction] = Settings.DEFAULT_AUDIO_FPS.value, # 44_100 before # 48_000.0 for aac
        # TODO: I don't like this name
        # TODO: Where does this come from (?)
        audio_samples_per_frame: int = Settings.DEFAULT_AUDIO_SAMPLES_PER_FRAME.value, # 1_024 before
        video_codec: str = Settings.DEFAULT_VIDEO_CODEC.value, # h264 before
        video_pixel_format: str = Settings.DEFAULT_PIXEL_FORMAT.value, # yuv420p before
        audio_codec: str = Settings.DEFAULT_AUDIO_CODEC.value, # aac before
        audio_layout: str  = Settings.DEFAULT_AUDIO_LAYOUT.value, # stereo before
        audio_format: str = Settings.DEFAULT_AUDIO_FORMAT.value # fltp before
    ):
        size = (
            Settings.DEFAULT_VIDEO_SIZE.value
            if size is None else
            size
        )

        fps = (
            Settings.DEFAULT_VIDEO_FPS.value
            if fps is None else
            fps
        )

        audio_fps = (
            Settings.DEFAULT_AUDIO_FPS.value
            if audio_fps is None else
            audio_fps
        )

        audio_samples_per_frame = (
            # 48_000 is not working well, why?
            Settings.DEFAULT_AUDIO_SAMPLES_PER_FRAME.value
            if audio_samples_per_frame is None else
            audio_samples_per_frame
        )

        video_codec = (
            Settings.DEFAULT_VIDEO_CODEC.value
            if video_codec is None else
            video_codec
        )

        video_pixel_format = (
            Settings.DEFAULT_PIXEL_FORMAT.value
            if video_pixel_format is None else
            video_pixel_format
        )

        audio_codec = (
            Settings.DEFAULT_AUDIO_CODEC.value
            if audio_codec is None else
            audio_codec
        )

        audio_layout = (
            Settings.DEFAULT_AUDIO_LAYOUT.value
            if audio_layout is None else
            audio_layout
        )

        audio_format = (
            Settings.DEFAULT_AUDIO_FORMAT.value
            if audio_format is None else
            audio_format
        )

        # TODO: By now I'm having only video
        # tracks
        self._tracks: list[VideoTrack, AudioTrack] = []
        """
        All the tracks we are handling.
        """
        self.size: tuple[int, int] = size
        """
        The size that the final video must have.
        """
        self.fps: Union[int, float, Fraction] = fps
        """
        The fps of the output video.
        """
        self.audio_fps: Union[int, Fraction] = audio_fps
        """
        The fps of the output audio.
        """
        self.audio_samples_per_frame: int = audio_samples_per_frame
        """
        The audio samples each audio frame must
        have.
        """
        self.video_codec: str = video_codec
        """
        The video codec for the video exported.
        """
        self.video_pixel_format: str = video_pixel_format
        """
        The pixel format for the video exported.
        """
        self.audio_codec: str = audio_codec
        """
        The codec for the audio exported.
        """
        self.audio_layout: str = audio_layout
        """
        The layout of the audio exported.
        """
        self.audio_format: str = audio_format
        """
        The format of the audio exported.
        """

        # We will have 2 video tracks by now
        self.add_video_track().add_video_track()

    def _add_track(
        self,
        index: Union[int, None] = None,
        is_audio: bool = False
    ) -> 'Timeline':
        """
        *For internal use only*

        Add a new track to the timeline that will
        be placed in the last position (highest 
        index, lowest priority).

        It will be a video track unless you send
        the 'is_audio' parameter as True.
        """
        number_of_tracks = (
            self.number_of_audio_tracks
            if is_audio else
            self.number_of_video_tracks
        )

        tracks = (
            self.audio_tracks
            if is_audio else
            self.video_tracks
        )

        index = (
            index
            if (
                index is not None and
                index < number_of_tracks
            ) else
            number_of_tracks
        )

        # We need to change the index of the
        # affected tracks (the ones that are
        # in that index and after it)
        if index < number_of_tracks:
            for track in tracks:
                if track.index >= index:
                    track.index += 1

        track = (
            AudioTrack(
                index = index,
                fps = self.fps,
                audio_fps = self.audio_fps,
                audio_samples_per_frame = self.audio_samples_per_frame,
                audio_layout = self.audio_layout, # stereo previously
                audio_format = self.audio_format # fltp previously
            )
            if is_audio else
            VideoTrack(
                index = index,
                size = self.size,
                fps = self.fps,
                audio_fps = self.audio_fps,
                audio_samples_per_frame = self.audio_samples_per_frame,
                audio_layout = self.audio_layout, # stereo previously
                audio_format = self.audio_format # fltp previously
            )
        )
            
        self._tracks.append(track)

        return self

    def add_video_track(
        self,
        index: Union[int, None] = None
    ) -> 'Timeline':
        """
        Add a new video track to the timeline, that
        will be placed in the last position (highest
        index, lowest priority).
        """
        return self._add_track(
            index = index,
            is_audio = False
        )
    
    def add_audio_track(
        self,
        index: Union[int, None] = None
    ) -> 'Timeline':  
        """
        Add a new audio track to the timeline, that
        will be placed in the last position (highest
        index, lowest priority).
        """  
        return self._add_track(
            index = index,
            is_audio = True
        )
    
    # TODO: Create a 'remove_track'

    def add_video(
        self,
        video: Union[VideoFileMedia, VideoImageMedia, VideoColorMedia],
        t: Union[int, float, Fraction, None] = None,
        track_index: int = 0
    ) -> 'Timeline':
        """
        Add the provided 'video' to the track with
        the given 'track_index' of this timeline,
        starting at the provided 't' time moment.

        If 'video' is not an instance of the
        VideoFileMedia class, the audio attributes
        will be forced to match the ones in this
        Timeline instance to generate the silent
        frames according to its configuration.
        """
        ParameterValidator.validate_mandatory_instance_of('video', video, [VideoFileMedia, VideoImageMedia, VideoColorMedia])
        ParameterValidator.validate_mandatory_number_between('track_index', track_index, 0, self.number_of_tracks)

        if track_index >= self.number_of_video_tracks:
            raise Exception(f'The "track_index" {str(track_index)} provided does not exist in this timeline.')

        """
        When we generate a video from a static source
        (VideoImageMedia, VideoColorMedia or
        VideoNumpyMedia) we need to force the audio
        attributes to match the ones from the timeline
        to generate the silent audio frames properly.
        """
        if PythonValidator.is_instance_of(video, [VideoImageMedia, VideoColorMedia]):
            video.source.audio_fps = self.audio_fps
            video.source.audio_samples_per_frame = self.audio_samples_per_frame

        # We need to force the output size to fit
        # the expected on the timeline
        video.set_output_size(self.size)

        # TODO: This should be, maybe, looking for
        # tracks by using the index property, not
        # as array index, but by now it is like
        # this as it is not very robust yet
        self.video_tracks[track_index].add_media(video, t)

        return self
    
    # TODO: Create a 'remove_video' 
    # TODO: Create a 'add_audio'
    # TODO: Create a 'remove_audio'
    
    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction],
        format: str = 'rgb24'
    ) -> 'VideoFrame':
        """
        Get all the frames that are played at the
        't' time provided, but combined in one.
        """
        # Frames come ordered by track index (priority)
        frames: list['VideoFrameWrapped'] = list(
            track.get_video_frame_at_t(t)
            for track in self.video_tracks
        )

        output_frame = None
        for frame in frames:
            # output_frame = (
            #     np.zeros(frame.as_rgba_numpy.shape, dtype = np.uint8)
            #     if output_frame is None else
            #     output_frame
            # )

            """
            The 'timeline' has a size that we must respect so
            we need to use a strategy to make the frame fit
            that size.
            """
            from yta_editor.utils.frame_wrapper import VideoFrameWrapped
            from yta_constants.ffmpeg import FfmpegPixelFormat

            print(frame.as_rgba_numpy.shape)
            print(frame._frame.format.name)

            output_frame = (
                VideoUtils.video.frame.combine_numpy_videoframes_with_alpha_layer(
                    top_frame = output_frame,
                    bottom_frame = frame.as_rgba_numpy
                )
                if output_frame is not None else
                frame.as_rgba_numpy
                #np.zeros(frame.as_rgba_numpy.shape, dtype = np.uint8)
            )

            if not frame.has_alpha_pixels:
                break

        # We add a completely black and transparent
        # frame at the end
        VideoUtils.video.frame.combine_numpy_videoframes_with_alpha_layer(
            top_frame = output_frame,
            bottom_frame = np.zeros(output_frame.shape, dtype = np.uint8)
        )

        # TODO: This was working previously (but
        # not as it should)

        # output_frame = None
        # # Boolean to avoid unnecessary calculations
        # output_frame_is_empty = False
        
        # for frame in frames:
        #     base_shape = frames[0].as_rgba_numpy.shape

        #     """
        #     These are the possibilities:
        #     1. Frame is from empty part
        #         - It is a completely transparent frame
        #     2. Frame is not from empty part
        #         - It can have or have not transparency
        #     """

        #     if frame.is_from_empty_part == True:
        #         # Completely black and transparent frame
        #         # 1. No previous frame => create a black one
        #         if output_frame is None:
        #             output_frame = np.zeros(base_shape, dtype = np.uint8)
        #             output_frame_is_empty = True
        #     else:
        #         # Frame has (or has not) some transparent
        #         # pixels but is not an empty frame
        #         if (
        #             output_frame is None or
        #             output_frame_is_empty
        #         ):
        #             output_frame = frame.as_rgba_numpy
        #             output_frame_is_empty = False
        #         else:
        #             # TODO: I think we should always combine
        #             # a black background (empty frame) as the
        #             # last element to avoid problems with the
        #             # transparency. If we have a completely
        #             # transparent color frame, it will be 
        #             # shown as a color frame, but it is 
        #             # completely transparent and should not be
        #             # visible...
        #             output_frame = VideoUtils.video.frame.combine_numpy_videoframes_with_alpha_layer(
        #                 top_frame = output_frame,
        #                 bottom_frame = frame.as_rgba_numpy
        #             )

        #         # If the last frame we add doesn't have
        #         # alpha pixels, as it has more priority
        #         # than the next ones, we can stop because
        #         # we have nothing to combine and we will
        #         # waste time
        #         if not frame.has_alpha_pixels:
        #             break

        # Now process according to the output
        # format
        output_frame = (
            # 1. Format accepts alpha but we don't have
            # it => add full opaque alpha layer
            np.concatenate(
                [
                    output_frame,
                    np.full(
                        shape = (output_frame.shape[0], output_frame.shape[1], 1),
                        fill_value = 255,
                        dtype = output_frame.dtype
                    )
                ],
                axis = -1
            )
            if (
                'a' in format and
                output_frame.shape[-1] == 3
            ) else
            # 2. Format doesn't accept alpha but we have
            # it => remove the alpha layer we have
            output_frame[..., :3]
            if (
                'a' not in format and
                output_frame.shape[-1] == 4
            ) else
            output_frame
        )

        # We first create it as 'rgb24' or 'rgba' and
        # then reformat to the expected format so we
        # only handle RGB/RGBA numpy arrays in code
        temp_format = (
            'rgba'
            if 'a' in format else
            'rgb24'
        )

        output_frame = VideoFrame.from_ndarray(
            array = output_frame,
            format = temp_format
        )

        return (
            output_frame.reformat(format = format)
            if format not in ['rgba', 'rgb24'] else
            output_frame
        )
    
    def get_audio_frames_at_t(
        self,
        t: float
    ):
        audio_frames: list[AudioFrameWrapped] = []
        """
        Matrix in which the rows are the different
        tracks we have, and the column includes all
        the audio frames for this 't' time moment
        for the track of that row. We can have more
        than one frame per column per row (track)
        but we need a single frame to combine all
        the tracks.
        """
        # TODO: What if the different audio streams
        # have also different fps (?)
        # We use both tracks because videos and
        # audio tracks have both audios
        for track in self.tracks:
            # TODO: Make this work properly
            audio_frames.append(list(track.get_audio_frames_at_t(t)))

        # TODO: I am receiving empty array here []
        # that doesn't include any frame in a specific
        # track that contains a video, why (?)
        print(audio_frames)

        # We need only 1 single audio frame per column
        collapsed_frames = [
            concatenate_audio_frames(frames)
            for frames in audio_frames
        ]

        # TODO: What about the lenghts and those
        # things? They should be ok because they are
        # based on our output but I'm not completely
        # sure here..
        print(collapsed_frames)

        # We keep only the non-silent frames because
        # we will sum them after and keeping them
        # will change the results.
        non_empty_collapsed_frames = [
            frame._frame
            for frame in collapsed_frames
            if not frame.is_from_empty_part
        ]

        if len(non_empty_collapsed_frames) == 0:
            # If they were all silent, just keep one
            non_empty_collapsed_frames = [collapsed_frames[0]._frame]

        # Now, mix column by column (track by track)
        # TODO: I do this to have an iterator, but 
        # maybe we need more than one single audio
        # frame because of the size at the original
        # video or something...
        frames = [
            AudioFrameCombinator.sum_tracks_frames(
                tracks_frames = non_empty_collapsed_frames,
                sample_rate = self.audio_fps,
                # TODO: This was not being sent before
                layout = self.audio_layout,
                format = self.audio_format
            )
        ]

        for audio_frame in frames:
            yield audio_frame
            
    def render(
        self,
        output_filename: str = 'test_files/output_render.mp4',
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None,
        output_format: str = 'yuv420p'
    ) -> 'Timeline':
        """
        Render the time range in between the given
        'start' and 'end' and store the result with
        the also provided 'fillename'.

        If no 'start' and 'end' provided, the whole
        project will be rendered.
        """
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_positive_number('end', end, do_include_zero = False)

        end = (
            self.end
            if end is None else
            end
        )

        # Limit 'end' a bit...
        if end >= 300:
            raise Exception('More than 5 minutes not supported yet.')

        if start >= end:
            raise Exception('The provided "start" cannot be greater or equal to the "end" provided.')
        
        # TODO: Accept 'argb' for 'qtrle' and '.mov'
        # Validator.validate_filename_for_output_video_format(
        #     filename = output_filename,
        #     format = output_format
        # )

        writer = VideoWriter(output_filename)

        # TODO: This has to be dynamic according to the
        # video we are writing (?)
        writer.set_video_stream(
            codec_name = self.video_codec,
            fps = self.fps,
            size = self.size,
            pixel_format = self.video_pixel_format
        )
        
        writer.set_audio_stream(
            codec_name = self.audio_codec,
            fps = self.audio_fps
        )
        # TODO: Maybe 'audio_format' and 'audio_layout' (?)

        time_base = fps_to_time_base(self.fps)
        audio_time_base = fps_to_time_base(self.audio_fps)

        audio_pts = 0
        for t in get_ts(start, end, self.fps):
            # TODO: According to the output extension
            # (or maybe a method parameter) we should
            # handle the format to include or not the
            # alpha layer
            frame = self.get_video_frame_at_t(
                t = t,
                format = output_format
            )
            # TODO: Frame could be None here if no video
            # in the media provided

            print(f'Getting t:{str(float(t))}')

            # We need to adjust our output elements to be
            # consecutive and with the right values
            # TODO: We are using int() for fps but its float...
            frame.time_base = time_base
            frame.pts = T(t, time_base).truncated_pts

            writer.mux_video_frame(
                frame = frame
            )

            for audio_frame in self.get_audio_frames_at_t(t):
                # TODO: 'audio_frame' could be None or []
                # here if no audio channel
                if audio_frame is None:
                    # TODO: Generate silence audio to cover the
                    # whole video frame (?)
                    pass
                
                # We need to adjust our output elements to be
                # consecutive and with the right values
                # TODO: We are using int() for fps but its float...
                audio_frame.time_base = audio_time_base
                audio_frame.pts = audio_pts

                # We increment for the next iteration
                audio_pts += audio_frame.samples

                writer.mux_audio_frame(audio_frame)

        writer.mux_video_frame(None)
        writer.mux_audio_frame(None)
        writer.output.close()

# TODO: Refactor and move please
# TODO: This has to work for AudioFrame
# also, but I need it working for Wrapped
def concatenate_audio_frames(
    frames: list[AudioFrameWrapped]
) -> AudioFrameWrapped:
    """
    Concatenate all the given 'frames' in one
    single audio frame and return it.

    The audio frames must have the same layout
    and sample rate.
    """
    if not frames:
        # TODO: This should not happen
        return None
    
    if len(frames) == 1:
        return frames[0]

    # We need to preserve the metadata
    is_from_empty_part = all(
        frame.is_from_empty_part
        for frame in frames
    )
    metadata = reduce(lambda key_values, frame: {**key_values, **frame.metadata}, frames, {})
    
    sample_rate = frames[0]._frame.sample_rate
    layout = frames[0]._frame.layout.name

    arrays = []
    # TODO: What about 'metadata' (?)
    for frame in frames:
        if (
            frame._frame.sample_rate != sample_rate or
            frame._frame.layout.name != layout
        ):
            raise ValueError("Los frames deben tener mismo sample_rate y layout")

        # arr = frame.to_ndarray()  # (channels, samples)
        # if arr.dtype == np.int16:
        #     arr = arr.astype(np.float32) / 32768.0
        # elif arr.dtype != np.float32:
        #     arr = arr.astype(np.float32)

        arrays.append(frame._frame.to_ndarray())

    combined = np.concatenate(arrays, axis = 1)

    out = AudioFrame.from_ndarray(
        array = combined,
        format = frames[0].format,
        layout = layout
    )
    out.sample_rate = sample_rate

    return AudioFrameWrapped(
        frame = out,
        metadata = metadata,
        is_from_empty_part = is_from_empty_part
    )