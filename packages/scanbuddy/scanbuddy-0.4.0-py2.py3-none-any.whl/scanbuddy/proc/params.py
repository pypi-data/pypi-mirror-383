import os
import logging
from pubsub import pub

logger = logging.getLogger(__name__)

class Params:
    def __init__(self, config, broker=None, debug=False):
        self._config = config.find_one('$.modalities', dict())
        self._broker = broker
        self._debug = debug
        self._coil_checked = False
        self._table_checked = False
        pub.subscribe(self.listener, 'params')
        pub.subscribe(self.reset, 'reset')

    def reset(self):
        self._coil_checked = False
        self._table_checked = False

    def listener(self, ds, modality):
        config = self._config[modality]['params']
        series_number = ds.get('SeriesNumber', 'UNKNOWN SERIES')
        instance_number = ds.get('InstanceNumber', 'UNKNOWN INSTANCE')
        logger.info(f'params listener fired for series={series_number}, instance={instance_number}')
        if self._coil_checked:
            logger.info(f'already checked coil from series={series_number}')
            return
        if self._table_checked:
            logger.info(f'already checked table table position from series={series_number}')
            return
        for item in config:
            logger.info(f'item is: {item}')
            args = config[item]
            f = getattr(self, item)
            f(ds, args)

    def coil_elements(self, ds, args):
        patient_name = ds.get('PatientName', 'UNKNOWN PATIENT')
        series_number = ds.get('SeriesNumber', 'UNKNOWN SERIES')
        instance_number = ds.get('InstanceNumber', 'UNKNOWN INSTANCE')
        logger.info(f'checking coil elements for series={series_number}, instance={instance_number}')
        self._coil_checked = True
        receive_coil = self.findcoil(ds)
        coil_elements = self.findcoilelements(ds)
        message = args['message'].format(
            SESSION=patient_name,
            SERIES=series_number,
            RECEIVE_COIL=receive_coil,
            COIL_ELEMENTS=coil_elements
        )
        for bad in args['bad']:
            a = ( receive_coil, coil_elements )
            b = ( bad['receive_coil'], bad['coil_elements'] )
            logger.info(f'checking if {a} == {b}')
            if a == b:
                logger.warning(message)
                logger.info(f'publishing message to message broker')
                self._broker.publish('scanbuddy_messages', message)
                break

    def table_position(self, ds, args):
        patient_name = ds.get('PatientName', 'UNKNOWN PATIENT')
        series_number = ds.get('SeriesNumber', 'UNKNOWN SERIES')
        instance_number = ds.get('InstanceNumber', 'UNKNOWN INSTANCE')
        logger.info(f'checking table position for series={series_number}, instance={instance_number}')
        self._table_checked = True
        table_position = self.find_table_position(ds)
        receive_coil = self.findcoil(ds)
        message = args['message'].format(
            SESSION=patient_name,
            SERIES=series_number,
            TABLE_POSITION=table_position,
        )
        for bad in args['bad']:
            a = (receive_coil, table_position)
            b = (bad['receive_coil'], bad['table_position'])
            logger.info(f'checking if {a} == {b}')
            if a == b:
                logger.warning(message)
                logger.info('publishing message to message broker')
                self._broker.publish('scanbuddy_messages', message)
                break

    def find_table_position(self, ds):
        seq = ds[(0x5200, 0x9230)][0]
        seq = seq[(0x0021, 0x11fe)][0]
        return seq[(0x0021, 0x1145)].value[-1]

    def findcoil(self, ds):
        seq = ds[(0x5200, 0x9229)][0]
        seq = seq[(0x0018, 0x9042)][0]
        return seq[(0x0018, 0x1250)].value
   
    def findcoilelements(self, ds):
        seq = ds[(0x5200, 0x9230)][0]
        seq = seq[(0x0021, 0x11fe)][0]
        return seq[(0x0021, 0x114f)].value

