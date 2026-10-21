"""Regression checks for the preserved installed customizations."""
import os
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import pytest
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QApplication

from labelImgPlusPlus import MainWindow
from libs.core.settings import Settings
from libs.core.shape import Shape
from libs.core.shortcut_config import ShortcutConfig


@pytest.fixture
def window(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    original_init = Settings.__init__

    def isolated_init(settings):
        original_init(settings)
        settings.path = str(tmp_path / 'settings.json')

    monkeypatch.setattr(Settings, '__init__', isolated_init)
    win = MainWindow()
    yield win
    win.set_clean()
    win.close()
    win.deleteLater()
    app.processEvents()


def test_custom_shortcuts_migrate_original_defaults():
    config = ShortcutConfig()
    config.from_dict({'delete': 'Delete', 'edit_label': 'Ctrl+E'})
    assert config.get('delete') == '0'
    assert config.get('edit_label') == 'Alt+C'
    config.from_dict({'delete': 'Alt+D'})
    assert config.get('delete') == 'Alt+D'


def test_display_controls_and_center_marker_preserve_geometry(window):
    shape = Shape('ball')
    for x, y in ((20, 20), (100, 20), (100, 100), (20, 100)):
        shape.add_point(QPointF(x, y))
    shape.close()
    window.canvas.shapes = [shape]
    original = [(p.x(), p.y()) for p in shape.points]
    window._set_label_font_size(64)
    window._set_box_line_width(4)
    window.show_bbox_center_checkbox.setChecked(True)
    assert window.label_font_size_slider.value() == 64
    assert window.label_font_size_dock_slider.value() == 64
    assert Shape.line_width == 4
    assert Shape.show_center_circle
    assert window.display_label_option.isChecked()
    image = QImage(160, 160, QImage.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    try:
        shape.paint(painter)
    finally:
        painter.end()
    assert image.pixelColor(60, 60).alpha() > 0
    assert [(p.x(), p.y()) for p in shape.points] == original


def test_dataset_classes_replace_packaged_classes(window, tmp_path):
    (tmp_path / 'classes.txt').write_text('ball\nplayer\nball\n', encoding='utf8')
    assert window._reload_dataset_classes(str(tmp_path))
    assert window.label_hist == ['ball', 'player']
    assert window.default_label == 'ball'
    window.rect_label_list.addItems(['ball', 'player', 'ball'])
    window._update_class_counts()
    assert window.class_count_label.text() == 'Instances per class: ball: 2, player: 1'


def test_clean_autosave_navigation_does_not_request_save_directory(window):
    window.auto_saving.setChecked(True)
    window.default_save_dir = None
    window.set_clean()
    with patch.object(window, 'change_save_dir_dialog') as dialog:
        window.open_next_image()
        window.open_prev_image()
    dialog.assert_not_called()


def test_delete_image_removes_individual_annotation(window, tmp_path):
    image_path = tmp_path / 'frame.png'
    annotation_path = tmp_path / 'frame.txt'
    image = QImage(32, 32, QImage.Format_RGB32)
    image.fill(0)
    assert image.save(str(image_path))
    annotation_path.write_text('0 0.5 0.5 0.2 0.2\n')
    window.file_path = str(image_path)
    window.last_open_dir = str(tmp_path)
    window.default_save_dir = str(tmp_path)
    window.cur_img_idx = 0
    window.delete_image()
    assert not image_path.exists()
    assert not annotation_path.exists()
