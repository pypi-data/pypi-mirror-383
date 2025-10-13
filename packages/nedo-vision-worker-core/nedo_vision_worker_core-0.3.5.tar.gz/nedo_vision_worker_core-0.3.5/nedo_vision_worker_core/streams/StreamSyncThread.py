import logging
import os
import time
import threading
from ..database.DatabaseManager import DatabaseManager
from ..repositories.WorkerSourceRepository import WorkerSourceRepository
from .VideoStreamManager import VideoStreamManager

class StreamSyncThread(threading.Thread):
    """Thread responsible for synchronizing video streams from the database in real-time."""

    def __init__(self, manager: VideoStreamManager, polling_interval=5):
        super().__init__()  # Set as a daemon so it stops with the main process

        self.source_file_path = DatabaseManager.STORAGE_PATHS["files"] / "source_files"

        self.manager = manager
        self.polling_interval = polling_interval
        self.worker_source_repo = WorkerSourceRepository()
        self.running = True

    def _get_source_file_path(self, file):
        """Returns the file path for a given source file."""
        return self.source_file_path / os.path.basename(file)

    def run(self):
        """Continuously updates the VideoStreamManager with database changes."""
        while self.running:
            try:
                sources = self.worker_source_repo.get_worker_sources()
                db_sources = {
                    source.id: 
                        source.url if source.type_code == "live" 
                        else source.url if source.type_code == "direct"
                        else self._get_source_file_path(source.file_path)
                     for source in sources
                }  # Store latest sources
                
                # Get both active streams and pending streams
                active_stream_ids = set(self.manager.get_active_stream_ids())
                with self.manager._lock:
                    pending_stream_ids = set(self.manager.pending_streams.keys())
                registered_stream_ids = active_stream_ids | pending_stream_ids

                # **1️⃣ Register new streams (lazy loading - don't start them yet)**
                for source_id, url in db_sources.items():
                    if source_id not in registered_stream_ids:
                        logging.info(f"🟢 Registering new stream: {source_id} ({url})")
                        self.manager.register_stream(source_id, url)

                # **2️⃣ Unregister deleted or disconnected streams**
                for stream_id in registered_stream_ids:
                    if stream_id not in db_sources:
                        logging.info(f"🔴 Unregistering stream: {stream_id}")
                        self.manager.unregister_stream(stream_id)

                # Refresh registered streams
                with self.manager._lock:
                    pending_stream_ids = set(self.manager.pending_streams.keys())
                registered_stream_ids = active_stream_ids | pending_stream_ids

                # **3️⃣ Update streams if URL has changed**
                for source_id, url in db_sources.items():
                    if source_id in registered_stream_ids:
                        # Check if it's an active stream or pending stream
                        with self.manager._lock:
                            is_pending = source_id in self.manager.pending_streams
                            if is_pending:
                                existing_url = self.manager.pending_streams.get(source_id)
                            else:
                                existing_url = None
                        
                        if existing_url is None:
                            # It's an active stream, get URL from stream manager
                            existing_url = self.manager.get_stream_url(source_id)
                        
                        # Only update if URL actually changed
                        if existing_url != url:
                            if is_pending:
                                # It's pending, just update the URL
                                with self.manager._lock:
                                    self.manager.pending_streams[source_id] = url
                                    logging.info(f"🟡 Updated pending stream {source_id} URL")
                            else:
                                # It's active, need to restart it
                                logging.info(f"🟡 Updating active stream {source_id}: New URL {url}")
                                # Unregister and re-register with new URL
                                self.manager.unregister_stream(source_id)
                                # Add a small delay for device cleanup
                                if self._is_direct_device(url) or self._is_direct_device(existing_url):
                                    time.sleep(0.5)  # Allow device to be properly released
                                self.manager.register_stream(source_id, url)

            except Exception as e:
                logging.error(f"⚠️ Error syncing streams from database: {e}")

            time.sleep(self.polling_interval)  # Poll every X seconds

    def _is_direct_device(self, url) -> bool:
        """Check if URL represents a direct video device."""
        if isinstance(url, str):
            return url.isdigit() or url.startswith('/dev/video')
        return isinstance(url, int)

    def stop(self):
        """Stops the synchronization thread."""
        self.running = False
