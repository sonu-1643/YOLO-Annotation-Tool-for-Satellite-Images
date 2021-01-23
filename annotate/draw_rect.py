#!/usr/bin/python
# -*- coding: utf-8 -*-

"""/***************************************************************************

This function helps to draw bounding boxes in QGIS
                              -------------------
        begin                : 2020-04-21
        git sha              : $Format:%H$
        copyright            : (C) 2020 by sonu dileep
        email                : sonudilp@colostate.edu
 ***************************************************************************/"""

from __future__ import print_function
from builtins import str
from builtins import range
from qgis.core import QgsWkbTypes, QgsPointXY

from qgis.PyQt.QtCore import Qt, QCoreApplication, pyqtSignal, QPoint
from qgis.PyQt.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, \
    QGridLayout, QLabel, QGroupBox, QVBoxLayout, QComboBox, \
    QPushButton, QInputDialog
from math import sqrt, pi, cos, sin
from qgis.core import QgsRectangle, QgsFeature, QgsVectorLayer, \
    QgsPoint, QgsGeometry, QgsFillSymbol, QgsGeometry, QgsMapSettings, \
    QgsPrintLayout, QgsMapSettings, QgsMapRendererParallelJob, \
    QgsLayoutItemLabel, QgsLayoutItemLegend, QgsLayoutItemMap, \
    QgsLayoutItemPolygon, QgsLayoutItemScaleBar, QgsLayoutExporter, \
    QgsLayoutItem, QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes, \
    QgsProject, QgsFillSymbol, QgsVectorLayer, QgsPoint, QgsPointXY, \
    QgsProject, QgsGeometry, QgsMapRendererJob

from qgis.PyQt.QtGui import QDoubleValidator, QIntValidator, \
    QKeySequence, QPolygonF, QColor

from qgis.PyQt.QtCore import Qt, QPointF, QRectF, QSize

from qgis.gui import QgsMapTool, QgsRubberBand, QgsMapToolEmitPoint, \
    QgsProjectionSelectionDialog, QgsMapCanvas, QgsVertexMarker, \
    QgsMapCanvasItem, QgsRubberBand


class RectangleMapTool(QgsMapToolEmitPoint):

    """Used to draw bounding boxes in QGIS"""

    selectionDone = pyqtSignal()
    move = pyqtSignal()

    def __init__(self, canvas, name):
        self.canvas = canvas
        self.name = name
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas,
                QgsWkbTypes.PolygonGeometry)
        self.couleur = QColor(151, 255, 255)
        self.couleur.setAlpha(100)
        self.rubberBand.setColor(self.couleur)
        self.rubberBand.setWidth(3)
        self.reset()
        self.initial = None
        self.end = None
        self.canvas = QgsMapCanvas()

    def reset(self):
        """reset the drawing"""

        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(True)

    def canvasPressEvent(self, e):
        """Activates on mouse click when user starts drawing the bounding box"""

        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True

    # self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        """Activates on mouse release when user is done with drawing"""

        self.isEmittingPoint = False
        r = self.rectangle()
        if r is not None:
            print('Rectangle:', r.xMinimum(), r.yMinimum(),
                  r.xMaximum(), r.yMaximum())

    def canvasMoveEvent(self, e):
        """Tracks the movement of mouse to find the size of bounding box"""

        if not self.isEmittingPoint:
            return
        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)

    def showRect(self, startPoint, endPoint):
        """Shows the drawn rectangle"""

        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        if startPoint.x() == endPoint.x() or startPoint.y() \
            == endPoint.y():
            return

        point1 = QgsPointXY(startPoint.x(), startPoint.y())
        point2 = QgsPointXY(startPoint.x(), endPoint.y())
        point3 = QgsPointXY(endPoint.x(), endPoint.y())
        point4 = QgsPointXY(endPoint.x(), startPoint.y())

        self.initial = startPoint
        self.end = endPoint

        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        self.rubberBand.addPoint(point4, True)  # true to update canvas

    def rectangle(self):
        """Specify the coordinate system and properties of rectangle(Color, thickness)"""

        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() \
            or self.startPoint.y() == self.endPoint.y():
            return None

        rect = QgsRectangle(self.startPoint, self.endPoint)
        rectangleLayer = QgsVectorLayer('Polygon?crs=EPSG:3857',
                self.name, 'memory')
        rectangleLayerProvider = rectangleLayer.dataProvider()
        newFeat = QgsFeature()

        geom = QgsGeometry.fromWkt(rect.asWktPolygon())

        newFeat.setGeometry(geom)
        rectangleLayerProvider.addFeatures([newFeat])
        QgsProject.instance().addMapLayer(rectangleLayer)
        symbol = QgsFillSymbol.createSimple({'name': 'square',
                'color': '0,0,255,0', 'width_border': '0.8'})
        rectangleLayer.renderer().setSymbol(symbol)
        return rect

    def deactivate(self):
        """Deactivate Rubberband in QGIS"""

        QgsMapTool.deactivate(self)
        self.deactivated.emit()
        self.rubberBand.reset(True)
