# qgis imports
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
# from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (Qgis, QgsProcessingParameterBoolean, QgsProcessingParameterEnum, QgsProcessing, QgsFeatureSink,
                       QgsProcessingParameterFeatureSource, QgsProcessingParameterFeatureSink, QgsFeature, QgsWkbTypes,
                       QgsProcessingParameterField, QgsProcessingParameterString)
# plugin
from .point_layer_reader import PointLayerReader


class TrackSegmentCreatorAlgorithm(QgisAlgorithm):
    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    def __init__(self):
        super().__init__()

        # Constants used to refer to parameters and outputs. They will be
        # used when calling the algorithm from another algorithm, or when
        # calling from the QGIS console.

        self.alg_name = "Track segment creator"
        self.alg_display_name = "Track segment creator"
        self.alg_group = "GPX segment tools"

        self.INPUT = 'INPUT'
        self.TIMESTAMP_FIELD = 'TIMESTAMP_FIELD'
        # self.TIMESTAMP_FORMAT = 'TIMESTAMP_FORMAT'
        self.ATTRIBUTE_MODE = 'ATTRIBUTE_MODE'
        self.CALCULATE_MOTION_ATTRIBUTES = 'CALCULATE_MOTION_ATTRIBUTES'
        # self.USE_EPSG_4326 = 'USE_EPSG_4326'
        self.OUTPUT = 'OUTPUT'

        self.attribute_mode_options = ['Both', 'First', 'Last']

        self.point_layer_reader = PointLayerReader()

    def name(self):
        return self.alg_name

    def displayName(self):
        return self.alg_display_name

    def group(self):
        return self.alg_group

    # def tr(self, text):
    #     return self.tr("gpxsegmentimporter", text)

    def initAlgorithm(self, config=None):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        # self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Input gpx file'),
        #                                                       [QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              self.tr('Input point layer'),
                                                              [QgsProcessing.TypeVectorPoint],
                                                              None, False))
        self.addParameter(QgsProcessingParameterField(self.TIMESTAMP_FIELD,
                                                      self.tr('Timestamp field'),
                                                      parentLayerParameterName=self.INPUT,
                                                      # type=QgsProcessingParameterField.Any))
                                                      type=QgsProcessingParameterField.DateTime))
        # self.addParameter(QgsProcessingParameterString(self.TIMESTAMP_FIELD,
        #                                                self.tr('Timestamp field'),
        #                                                None, False, False))
        # self.addParameter(QgsProcessingParameterString(self.TIMESTAMP_FORMAT,
        #                                                self.tr('Timestamp format (applies only if \'Timestamp field\''
        #                                                        ' is of type string)'),
        #                                                '%Y-%m-%dT%H:%M:%S', False, True))
        self.addParameter(QgsProcessingParameterEnum(self.ATTRIBUTE_MODE,
                                                     self.tr('Add attributes from which segment track point(s)'),
                                                     options=self.attribute_mode_options,
                                                     allowMultiple=False, defaultValue=2, optional=False))
        self.addParameter(QgsProcessingParameterBoolean(self.CALCULATE_MOTION_ATTRIBUTES,
                                                        self.tr(
                                                            'Calculate distance, speed and duration between ' +
                                                            'track points'),
                                                        defaultValue=True, optional=True))
        # self.addParameter(QgsProcessingParameterBoolean(self.USE_EPSG_4326,
        #                                                 self.tr('Use \'EPSG:4326\' coordinate reference system'),
        #                                                 True, True))

        # We add a vector layer as output
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Output'),
                                                            QgsProcessing.TypeVectorLine))

    def processAlgorithm(self, parameters, context, feedback):
        pass
        source = self.parameterAsSource(parameters, self.INPUT, context)
        # if source is None:  # https://github.com/qgis/QGIS/blob/master/python/plugins/processing/algs/qgis/PointsLayerFromTable.py
        #     raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        timestamp_field = self.parameterAsString(parameters, self.TIMESTAMP_FIELD, context)
        # timestamp_format = self.parameterAsString(parameters, self.TIMESTAMP_FORMAT, context)
        attribute_mode = self.attribute_mode_options[self.parameterAsInt(parameters, self.ATTRIBUTE_MODE, context)]
        calculate_motion_attributes = self.parameterAsBool(parameters, self.CALCULATE_MOTION_ATTRIBUTES, context)
        # use_epsg4326 = self.parameterAsBool(parameters, self.USE_EPSG_4326, context)

        feedback.setProgress(0)
        layer = self.point_layer_reader.import_gpx_file(source, timestamp_field, "", attribute_mode,
                                                        calculate_motion_attributes)
        feedback.setProgress(100)
        if self.point_layer_reader.error_message != '':
            self.iface.messageBar().pushMessage("Error", self.gpx_file_reader.error_message,
                                                level=Qgis.CRITICAL)

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               layer.fields(), QgsWkbTypes.LineString, layer.sourceCrs())

        for f in layer.getFeatures():
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: dest_id}