from __future__ import annotations

import threading
import time
from avatar.messaging import StreamClient, IStreamClient
from avatar.daemon import SoundInjectionCommand, SoundCommand, SoundConfirmation, OpenMicCommand, VolumeCommand

from ..processing import IUnit, SystemSoundCommand, SystemSoundType, State, UnitInput, IMonitor
from ..outputs import IAudioOutput
from ..inputs import IAudioInput, FakeInput
from .events import *
from .volume import VolumeController
from pathlib import Path
from yo_fluq import FileIO
from .console_monitor import ConsoleMonitor
import traceback


REQUIRED_TYPES = (
    SoundCommand, SoundInjectionCommand,
    SystemSoundCommand, VolumeCommand,
    OpenMicCommand
)


class PhonixDeamon:
    def __init__(self,
                 client: StreamClient,
                 file_retriever: Optional[Callable[[str],bytes]],
                 input: IAudioInput,
                 output: IAudioOutput,
                 units: list[IUnit],
                 system_sounds: dict[SystemSoundType, bytes],
                 silent: bool = True,
                 tolerate_exceptions: bool = False,
                 async_messaging: bool = False
                ):
        self.base_client = client
        self.async_messaging = async_messaging
        self.client: IStreamClient|None = None

        self.file_retriever = file_retriever
        self.input: IAudioInput = input
        self.output = output
        self.units = list(units)
        self.system_sounds = system_sounds
        self.confirm_on_play_finishes: List[IMessage,...]|None = None
        self.confirm_on_injection_finishes: IMessage|None = None
        self.state = State(MicState.Standby)
        self._termination_requested = threading.Event()
        self.volume_controller: VolumeController|None = None
        self.monitor = IMonitor()
        if not silent:
            self.monitor = ConsoleMonitor()
        self.tolerate_exceptions = tolerate_exceptions




    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_termination_requested']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._termination_requested = threading.Event()

    def confirm_currently_playing(self, terminated: bool):
        ids = [message.envelop.id for message in self.confirm_on_play_finishes]
        message = SoundConfirmation(terminated).as_confirmation_for(ids)
        if len(ids) > 0:
            message = message.as_reply_to(ids[-1])
        self.client.put(message)
        self.confirm_on_play_finishes = None

    def start_playing(self, content, external_message, internal_message):
        if self.output.is_playing():
            self.output.cancel_playing()
            self.confirm_currently_playing(True)
        self.client.put(internal_message)
        self.output.start_playing(content)
        self.confirm_on_play_finishes = [external_message, internal_message]

    def parse_incoming_message(self, message):
        if isinstance(message, SoundCommand):
            content = self.file_retriever(message.file_id)
            self.start_playing(content, message, SoundPlayStarted(message.text).as_reply_to(message))
        if isinstance(message, SoundInjectionCommand):
            if not isinstance(self.input, FakeInput):
                self.input.stop()
                self.input = FakeInput()
            content = self.file_retriever(message.file_id)
            self.confirm_on_injection_finishes = message
            self.input.set_sample(content)
        if isinstance(message, SystemSoundCommand):
            if message.sound in self.system_sounds:
                self.start_playing(self.system_sounds[message.sound], message, SoundPlayStarted(message.sound.name).as_reply_to(message))
        if isinstance(message, VolumeCommand):
            if self.volume_controller is None:
                self.volume_controller = VolumeController()
            self.volume_controller.set(message.value)

        


    def iteration(self):
        messages = self.client.pull_all()

        open_mic_requested = False
        for message in messages:
            self.parse_incoming_message(message)
            if isinstance(message, OpenMicCommand):
                self.client.put(message.confirm_this())
                open_mic_requested = True

        if not self.output.is_playing() and self.confirm_on_play_finishes is not None:
            self.confirm_currently_playing(False)

        if isinstance(self.input, FakeInput) and self.input.is_buffer_empty() and self.confirm_on_injection_finishes is not None:
            self.client.put(self.confirm_on_injection_finishes.confirm_this())
            self.confirm_on_injection_finishes = None

        mic_data = self.input.read()

        messages_tuple = tuple(messages)
        for unit in self.units:
            input = UnitInput(self.state, mic_data, messages_tuple, open_mic_requested, self.monitor, self.client.put)
            state_change = unit.process(input)
            if state_change is not None:
                self.state = state_change
                self.client.put(MicStateChangeReport(state_change.mic_state))
                input.monitor.on_state_change(state_change)

    def _run_attempt(self, scroll_to_end_when_initializing):
        print("Connecting to avatar...")
        client= self.base_client.clone().with_types(*REQUIRED_TYPES)
        if scroll_to_end_when_initializing:
            client.scroll_to_end()
        if self.async_messaging:
            self.client = client.as_asyncronous()
        else:
            self.client = client
        self.client.initialize()
        print("OK")
        self.input.start()
        try:
            while not self._termination_requested.is_set():
                self.iteration()
                time.sleep(0.01)
        finally:
            self.input.stop()

    def run(self):
        if not self.tolerate_exceptions:
            self._run_attempt(False)
        else:
            while True:
                try:
                    self._run_attempt(True)
                except KeyboardInterrupt:
                    return
                except:
                    print(f"\nException:\n{traceback.format_exc()}")
                    print("Continuing")
                time.sleep(1)

    def run_in_thread(self):
        threading.Thread(target=self.run, daemon=True).start()

    def __call__(self):
        self.run()


    def terminate(self):
        self._termination_requested.set()


    @staticmethod
    def get_default_system_sounds() -> dict[SystemSoundType, bytes]:
        result = {}
        path = Path(__file__).parent/'files'
        result[SystemSoundType.opening] = FileIO.read_bytes(path/'beep_hi.wav')
        result[SystemSoundType.confirmation] = FileIO.read_bytes(path / 'beep_lo.wav')
        result[SystemSoundType.error] = FileIO.read_bytes(path / 'beep_error.wav')
        return result








