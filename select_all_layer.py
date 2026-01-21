from qgis.PyQt.QtGui import QColor
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsProject, QgsVectorLayer, QgsRectangle, QgsPointXY,QgsWkbTypes

class RectangleSelectAllLayers(QgsMapTool):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.start_point = None
        self.rubber_band = QgsRubberBand(canvas, QgsWkbTypes.PolygonGeometry)  # True = polygone
        self.rubber_band.setColor(QColor(255,0,0,100))
        self.rubber_band.setWidth(2)

    def canvasPressEvent(self, event):
        self.start_point = self.toMapCoordinates(event.pos())
        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
        self.rubber_band.addPoint(self.start_point, False)

    def canvasMoveEvent(self, event):
        if not self.start_point:
            return
        current_point = self.toMapCoordinates(event.pos())
        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
        self.rubber_band.addPoint(self.start_point, False)
        self.rubber_band.addPoint(QgsPointXY(current_point.x(), self.start_point.y()), False)
        self.rubber_band.addPoint(current_point, False)
        self.rubber_band.addPoint(QgsPointXY(self.start_point.x(), current_point.y()), True)

    def canvasReleaseEvent(self, event):
        if not self.start_point:
            return
        end_point = self.toMapCoordinates(event.pos())
        rect = QgsRectangle(self.start_point, end_point)
        print(rect)

        # Sélectionner toutes les entités dans ce rectangle pour tous les layers vecteurs
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer):
                ids = [f.id() for f in layer.getFeatures(rect)]
                layer.selectByIds(ids)

        # reset
        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
        self.start_point = None