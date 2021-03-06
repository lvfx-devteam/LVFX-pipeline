import os
import subprocess
import shlex
import threading
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

from PySide.phonon import Phonon


def async(fn):
    """Run *fn* asynchronously."""
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
    return wrapper


class VideoWidget(QtGui.QWidget):
    """ Video Player Widget """

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout())
        self.setMouseTracking(True)
        self.setAutoFillBackground(False)
        self.setup(parent)

    def setup(self, parent):
        self.media = Phonon.MediaObject(parent)
        videoWidget = Phonon.VideoWidget(parent)
        Phonon.createPath(self.media, videoWidget)
        self.layout().addWidget(videoWidget)
        self.seekSlider = Phonon.SeekSlider(self.media, parent)
        self.layout().addWidget(self.seekSlider)
        self.seekSlider.setIconVisible(False)
        self.media.finished.connect(self.mediaFinished)

    def setMediaSource(self, path):
        self.media.setCurrentSource(path)
        filename = os.path.split(path)[1]
        fname = os.path.splitext(filename)[0]
        label = QtGui.QLabel(fname)
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout().addWidget(label)
        self.media.play()
        self.media.pause()

    def mediaFinished(self):
        self.media.play()
        self.media.pause()

    def mousePressEvent(self, event):
        # Mouse press acts as a toggle to play or pause the media in the widget.
        super(VideoWidget, self).mousePressEvent(event)
        if self.media.state() == Phonon.State.PlayingState:
            self.media.pause()
        else:
            self.media.play()
        event.ignore()

    def mouseDoubleClickEvent(self, event):
        # On double click, open file in media player
        super(VideoWidget, self).mousePressEvent(event)
        self.playMovie(self.media.currentSource().fileName())
        event.ignore()

    @async
    def playMovie(self, outFile):
        # Opens the media file in the player in a different thread.
        mov_player = '/usr/bin/djv_view'
        try:
            cmd = '{0} "{1}"'.format(mov_player, outFile)
            args = shlex.split(cmd)
            subprocess.call(args)
        except Exception:
            mov_player = '/usr/bin/vlc'
            try:
                cmd = '{0} "{1}"'.format(mov_player, outFile)
                args = shlex.split(cmd)
                subprocess.call(args)
            except Exception:
                pass

