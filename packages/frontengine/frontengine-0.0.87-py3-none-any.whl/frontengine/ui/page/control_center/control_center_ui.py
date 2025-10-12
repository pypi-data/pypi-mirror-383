from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QGridLayout, QWidget, QPushButton, QTextEdit, QScrollArea

from frontengine.ui.color.global_color import error_color, output_color
from frontengine.ui.page.gif.gif_setting_ui import GIFSettingUI
from frontengine.ui.page.image.image_setting_ui import ImageSettingUI
from frontengine.ui.page.particle.particle_setting_ui import ParticleSettingUI
from frontengine.ui.page.scene_setting.scene_setting_ui import SceneSettingUI
from frontengine.ui.page.sound_player.sound_player_setting_ui import SoundPlayerSettingUI
from frontengine.ui.page.text.text_setting_ui import TextSettingUI
from frontengine.ui.page.video.video_setting_ui import VideoSettingUI
from frontengine.ui.page.web.web_setting_ui import WEBSettingUI
from frontengine.utils.logging.loggin_instance import front_engine_logger
from frontengine.utils.multi_language.language_wrapper import language_wrapper
from frontengine.utils.redirect_manager.redirect_manager_class import redirect_manager_instance


class ControlCenterUI(QWidget):

    def __init__(
            self,
            video_setting_ui: VideoSettingUI,
            image_setting_ui: ImageSettingUI,
            web_setting_ui: WEBSettingUI,
            gif_setting_ui: GIFSettingUI,
            sound_player_setting_ui: SoundPlayerSettingUI,
            text_setting_ui: TextSettingUI,
            scene_setting_ui: SceneSettingUI,
            particle_setting_ui: ParticleSettingUI,
            redirect_output:bool = True
    ):
        front_engine_logger.info("Init ControlCenterUI "
                                 f"video_setting_ui: {video_setting_ui} "
                                 f"image_setting_ui: {image_setting_ui} "
                                 f"web_setting_ui: {web_setting_ui} "
                                 f"gif_setting_ui: {gif_setting_ui} "
                                 f"sound_player_setting_ui: {sound_player_setting_ui} "
                                 f"text_setting_ui: {text_setting_ui} "
                                 f"scene_setting_ui: {scene_setting_ui} "
                                 f"particle_setting_ui: {particle_setting_ui} "
                                 f"redirect_output: {redirect_output}")
        super().__init__()
        # Layout
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # UI instance
        self.video_setting_ui = video_setting_ui
        self.image_setting_ui = image_setting_ui
        self.web_setting_ui = web_setting_ui
        self.gif_setting_ui = gif_setting_ui
        self.sound_player_setting_ui = sound_player_setting_ui
        self.text_setting_ui = text_setting_ui
        self.scene_setting_ui = scene_setting_ui
        self.particle_setting_ui = particle_setting_ui
        # Close video widget
        self.clear_video_button = QPushButton(
            language_wrapper.language_word_dict.get("control_center_close_all_video")
        )
        self.clear_video_button.clicked.connect(self.clear_video)
        # Close image widget
        self.clear_image_button = QPushButton(
            language_wrapper.language_word_dict.get("control_center_close_all_image")
        )
        self.clear_image_button.clicked.connect(self.clear_image)
        # Close gif widget
        self.clear_gif_button = QPushButton(
            language_wrapper.language_word_dict.get("control_center_close_all_gif")
        )
        self.clear_gif_button.clicked.connect(self.clear_gif)
        # Close web widget
        self.clear_web_button = QPushButton(
            language_wrapper.language_word_dict.get("control_center_close_all_web")
        )
        self.clear_web_button.clicked.connect(self.clear_web)
        # Close sound widget
        self.clear_sound_button = QPushButton(
            language_wrapper.language_word_dict.get("control_center_close_all_sound")
        )
        self.clear_sound_button.clicked.connect(self.clear_sound)
        # Close text widget
        self.clear_text_button = QPushButton(
            language_wrapper.language_word_dict.get("control_center_close_all_text")
        )
        self.clear_text_button.clicked.connect(self.clear_text)
        # Close scene widget
        self.clear_scene_button = QPushButton(
            language_wrapper.language_word_dict.get("control_center_scene")
        )
        self.clear_scene_button.clicked.connect(self.clear_scene)
        # Clear redirect
        self.clear_redirect_button = QPushButton(
            language_wrapper.language_word_dict.get("control_center_clear_log_panel")
        )
        self.clear_redirect_button.clicked.connect(self.clear_redirect)
        # Close chat scene
        self.clear_chat_button = QPushButton(
            language_wrapper.language_word_dict.get("chat_scene_close")
        )
        self.clear_chat_button.clicked.connect(self.clear_redirect)
        # All widget close
        self.clear_all_button = QPushButton(
            language_wrapper.language_word_dict.get("control_center_close_all")
        )
        self.clear_all_button.clicked.connect(self.clear_all)
        # Log panel
        self.log_panel = QTextEdit()
        self.log_panel.setLineWrapMode(self.log_panel.LineWrapMode.NoWrap)
        self.log_panel.setReadOnly(True)
        self.log_panel_scroll_area = QScrollArea()
        self.log_panel_scroll_area.setWidgetResizable(True)
        self.log_panel_scroll_area.setViewportMargins(0, 0, 0, 0)
        self.log_panel_scroll_area.setWidget(self.log_panel)
        # Add to layout
        self.grid_layout.addWidget(self.clear_video_button, 0, 0)
        self.grid_layout.addWidget(self.clear_image_button, 1, 0)
        self.grid_layout.addWidget(self.clear_gif_button, 2, 0)
        self.grid_layout.addWidget(self.clear_web_button, 3, 0)
        self.grid_layout.addWidget(self.clear_sound_button, 4, 0)
        self.grid_layout.addWidget(self.clear_text_button, 5, 0)
        self.grid_layout.addWidget(self.clear_redirect_button, 6, 0)
        self.grid_layout.addWidget(self.clear_all_button, 7, 0)
        self.grid_layout.addWidget(self.log_panel_scroll_area, 0, 1, -1, -1)
        self.setLayout(self.grid_layout)
        if redirect_output:
            # Redirect
            self.redirect_timer = QTimer(self)
            self.redirect_timer.setInterval(10)
            self.redirect_timer.timeout.connect(self.redirect)
            self.redirect_timer.start()
            redirect_manager_instance.set_redirect()

    def clear_video(self) -> None:
        front_engine_logger.info(f"ControlCenterUI clear_video")
        self.video_setting_ui.video_widget_list.clear()

    def clear_image(self) -> None:
        front_engine_logger.info(f"ControlCenterUI clear_image")
        self.image_setting_ui.image_widget_list.clear()

    def clear_gif(self) -> None:
        front_engine_logger.info("ControlCenterUI clear_gif")
        self.gif_setting_ui.gif_widget_list.clear()

    def clear_web(self) -> None:
        front_engine_logger.info("ControlCenterUI clear_web")
        self.web_setting_ui.web_widget_list.clear()

    def clear_sound(self) -> None:
        front_engine_logger.info("ControlCenterUI clear_sound")
        self.sound_player_setting_ui.sound_widget_list.clear()

    def clear_text(self) -> None:
        front_engine_logger.info("ControlCenterUI clear_text")
        self.text_setting_ui.text_widget_list.clear()

    def clear_redirect(self) -> None:
        front_engine_logger.info("ControlCenterUI clear_redirect")
        self.log_panel.clear()

    def clear_scene(self) -> None:
        front_engine_logger.info("ControlCenterUI clear_scene")
        self.scene_setting_ui.close_scene()

    def clear_all(self) -> None:
        front_engine_logger.info("ControlCenterUI clear_all")
        self.video_setting_ui.video_widget_list.clear()
        self.image_setting_ui.image_widget_list.clear()
        self.web_setting_ui.web_widget_list.clear()
        self.gif_setting_ui.gif_widget_list.clear()
        self.sound_player_setting_ui.sound_widget_list.clear()
        self.text_setting_ui.text_widget_list.clear()
        self.particle_setting_ui.particle_list.clear()
        self.scene_setting_ui.close_scene()

    def redirect(self) -> None:
        front_engine_logger.info("ControlCenterUI redirect")
        if not redirect_manager_instance.std_out_queue.empty():
            output_message = redirect_manager_instance.std_out_queue.get_nowait()
            output_message = str(output_message).strip()
            if output_message:
                self.log_panel.append(output_message)
        self.log_panel.setTextColor(error_color)
        if not redirect_manager_instance.std_err_queue.empty():
            error_message = redirect_manager_instance.std_err_queue.get_nowait()
            error_message = str(error_message).strip()
            if error_message:
                self.log_panel.append(error_message)
        self.log_panel.setTextColor(output_color)
