""" Perform C_MOVE action. """

from __future__ import annotations

import functools
import typing
from typing import Self

import pydicom
import pydicom.uid
from loguru import logger
from pynetdicom import AE, evt
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelMove  # type: ignore

from dicom_qr.echo import echo_scu
from dicom_qr.retrieve_utils import AssociationError, RetrieveResult, process_responses
from dicom_qr.scp import Anonymizer, dummy_anonymize, handle_store
from dicom_qr.settings import PacsConfig
from dicom_qr.storage_classes import StoragePresentationContexts, TRANSFER_SYNTAX
from dicom_qr.contexts import STRUCTURED_REPORT_STORAGE_CLASSES

if typing.TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Callable, Iterable
    from dicom_qr.database import SeriesData


class RetrievePacsMove:
    """ Retrieve images from PACS using C-MOVE.
    Based on [movescu.py](https://github.com/pydicom/pynetdicom/blob/main/pynetdicom/apps/movescu/movescu.py)
    """

    def __init__(self,
                 pacs_config: PacsConfig,
                 uid_mapping: Callable[[str], str],
                 retrieve_callback: Callable[[RetrieveResult], None],
                 folder_callback: Callable[[Path], None],
                 anonymizer: Anonymizer = dummy_anonymize,
                 sop_class_uid: Iterable[str] | None = None,
                 *,
                 store_scp: bool = True) -> None:
        self.pacs_config = pacs_config
        self._retrieve_callback = retrieve_callback

        self.application_entity = AE(ae_title=pacs_config.client_ae_title)
        self.application_entity.add_requested_context(StudyRootQueryRetrieveInformationModelMove)
        self.application_entity.supported_contexts = StoragePresentationContexts
        for uid in sorted(STRUCTURED_REPORT_STORAGE_CLASSES.values()):
            self.application_entity.add_supported_context(uid, TRANSFER_SYNTAX)

        self._create_storage(uid_mapping, anonymizer, sop_class_uid, folder_callback, store_scp=store_scp)

        self.assoc = self.application_entity.associate(addr=pacs_config.server_ae_ip, port=pacs_config.server_ae_port,
                                                       ae_title=pacs_config.server_ae_title)

        if not self.assoc.is_established:
            raise AssociationError('Association not established.')

    def _create_storage(self,
                        uid_mapping: Callable[[str], str],
                        anonymizer: Anonymizer,
                        sop_class_uid: Iterable[str] | None,
                        folder_callback: Callable[[Path], None],
                        *,
                        store_scp: bool) -> None:
        if not store_scp:
            try:
                # Check if a DICOM storage (C-STORE) SCP is present at the provided port
                echo_scu(PacsConfig(server_ae_ip='localhost',
                                    server_ae_title=self.pacs_config.client_ae_title,
                                    server_ae_port=self.pacs_config.client_ae_port,
                                    client_ae_title=self.pacs_config.client_ae_title))
            except RuntimeError as e:
                logger.error(f'No C-STORE SCP found at port: {self.pacs_config.client_ae_port}')
                raise RuntimeError from e
            return

        # Start a DICOM storage (C-STORE) SCP to handle incoming data and write to storage.
        handler_func = functools.partial(
            handle_store,
            base_folder=self.pacs_config.base_folder,
            folder_template=self.pacs_config.folder_template,
            anonimyzer=anonymizer,
            uid_mapping=uid_mapping,
            folder_callback=folder_callback,
            sop_class_uid=sop_class_uid
        )
        logger.debug(f'Starting C-STORE SCP. port={self.pacs_config.client_ae_port}')
        self.application_entity.start_server(
            ('', self.pacs_config.client_ae_port), block=False, evt_handlers=[(evt.EVT_C_STORE, handler_func)])

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.application_entity.shutdown()

    def retrieve(self, dataset: pydicom.Dataset) -> RetrieveResult | None:
        """ Retrieve images for a dataset. """
        if not self.assoc.is_established:
            logger.error('Association not established.')
            return None

        responses = self.assoc.send_c_move(dataset, self.pacs_config.client_ae_title,
                                           StudyRootQueryRetrieveInformationModelMove)

        return process_responses(responses, self._retrieve_callback)

    def retrieve_images_for_a_series(self, series_data: SeriesData) -> RetrieveResult | None:
        """ Retrieve images for a series. """
        dataset = pydicom.Dataset()
        dataset.QueryRetrieveLevel = 'SERIES'
        if series_data.StudyInstanceUID != 'NA':
            dataset.StudyInstanceUID = series_data.StudyInstanceUID
        dataset.SeriesInstanceUID = series_data.SeriesInstanceUID
        return self.retrieve(dataset)
