from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QGraphicsView

from frontengine.utils.logging.loggin_instance import front_engine_logger


class ExtendGraphicView(QGraphicsView):

    def __init__(self, *args):
        front_engine_logger.info("Init ExtendGraphicView "
                                 f"args: {args}")
        super().__init__(*args)
        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowType_Mask |
            Qt.WindowType.Tool
        )
        self.setStyleSheet("background:transparent")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def wheelEvent(self, event) -> None:
        if len(self.scene().items()) == 0:
            pass
        else:
            front_engine_logger.info("ExtendGraphicView wheelEvent"
                                     f"event: {event}")
            current_position = event.position()
            scene_position = self.mapToScene(QPoint(int(current_position.x()), int(current_position.y())))
            view_width = self.viewport().width()
            view_height = self.viewport().height()
            horizon_scale = current_position.x() / view_width
            vertical_scale = current_position.y() / view_height
            wheel_value = event.angleDelta().y()
            scale_factor = self.transform().m11()

            if (scale_factor < 0.5 and wheel_value < 0) or (scale_factor > 50 and wheel_value > 0):
                return

            if wheel_value > 0:
                self.scale(1.2, 1.2)
            else:
                self.scale(1.0 / 1.2, 1.0 / 1.2)

            view_point = self.transform().map(scene_position)
            self.horizontalScrollBar().setValue(int(view_point.x() - view_width * horizon_scale))
            self.verticalScrollBar().setValue(int(view_point.y() - view_height * vertical_scale))

            self.update()
