import os
from Settings.setup_logger import logging

LOGGER = logging.getLogger(__name__)

class helper:
    def downloadEdgarIndexFileAndGetPath(response, qtr, year):
        edgarIndexFileDownloadPath = f"{os.path.dirname(__file__)}\\resources\edgar-full-index-archives\master-{year}-QTR{qtr}.txt"
        LOGGER.info(f"Downloading the master Edgar Index File to: {edgarIndexFileDownloadPath}")

        with open(edgarIndexFileDownloadPath, "wb") as f:
            f.write(response.content)
        if not f.closed:
            try:
                os.remove(edgarIndexFileDownloadPath)
            except OSError as e:  
                LOGGER.info("Error downloading and processing the Edgar Index file - rerun as it now most likely contains corrupted data: %s - %s." % (e.filename, e.strerror))

        return edgarIndexFileDownloadPath