"""Test MKVFile object."""

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from nudebomb.config import NudebombConfig
from nudebomb.mkv import MKVFile
from tests.util import SRC_PATH, TEST_FN, DiffTracksTest, mkv_tracks

if TYPE_CHECKING:
    from confuse import AttrDict

__all__ = ()

TEST_DIR = Path("/tmp/nudebomb.test_remux")  # noqa: S108
TEST_MKV = TEST_DIR / TEST_FN


def assert_eng_und_only(out_tracks):
    """Asset english and undefined only tracks."""
    audio_count = 0
    subs_count = 0
    for track in out_tracks:
        track_type = track.get("type")
        if track_type not in MKVFile.REMOVABLE_TRACK_NAMES:
            continue
        lang = track["properties"]["language"]
        print(track_type, lang)
        assert lang in ["und", "eng"]
        if track_type == MKVFile.SUBTITLE_TRACK_NAME:
            subs_count += 1
        elif track_type == MKVFile.AUDIO_TRACK_NAME:
            audio_count += 1
        else:
            msg = f"Bad track type: {track_type}"
            raise AssertionError(msg)
    assert audio_count == 2  # noqa: PLR2004
    assert subs_count == 2  # noqa: PLR2004


class TestMkv(DiffTracksTest):
    """Test MKV."""

    def setup_method(self):
        """Set up method."""
        shutil.rmtree(TEST_DIR, ignore_errors=True)
        TEST_DIR.mkdir()
        shutil.copy(SRC_PATH, TEST_MKV)
        self.src_tracks: list = mkv_tracks(TEST_MKV)  #  pyright: ignore[reportUninitializedInstanceVariable]
        os.environ["NUDEBOMB_NUDEBOMB__LANGUAGES__0"] = "und"
        os.environ["NUDEBOMB_NUDEBOMB__LANGUAGES__1"] = "eng"
        self._config: AttrDict = NudebombConfig().get_config()  #  pyright: ignore[reportUninitializedInstanceVariable]

    def teardown_method(self):
        """Tear down method."""
        shutil.rmtree(TEST_DIR)

    def test_dry_run(self):
        """Test dry run."""
        self._config.dry_run = True
        mkvfile = MKVFile(self._config, TEST_MKV)
        mkvfile.remove_tracks()
        out_tracks = mkv_tracks(TEST_MKV)
        self._diff_tracks(out_tracks)

    def test_run(self):
        """Test run."""
        mkvfile = MKVFile(self._config, TEST_MKV)
        mkvfile.remove_tracks()
        out_tracks = mkv_tracks(TEST_MKV)
        assert_eng_und_only(out_tracks)

    def test_fail(self):
        """Test fail."""
        self._config.languages = ["xxx"]
        mkvfile = MKVFile(self._config, TEST_MKV)
        mkvfile.remove_tracks()
        out_tracks = mkv_tracks(TEST_MKV)
        self._diff_tracks(out_tracks)
