import sqlite3
from datetime import datetime
import os
import sys
import traceback
import logging


class RunTracker:

    def __init__(self, db_path: str, project_name: str = None, max_log_files: int = 10,
                 trigger_type: str = "scheduler"):
        """
        Initialize RunTracker

        Args:
            db_path: Path to the SQLite database
            project_name: Optional project name (defaults to script filename)
            max_log_files: Maximum number of log files to keep (default: 10)
            trigger_type: 'scheduler' or 'manual' - how the flow was triggered
        """
        self.db_path = db_path
        self.max_log_files = max_log_files
        self.trigger_type = trigger_type

        # Get the script path
        self.script_path = os.path.abspath(sys.argv[0])
        self.script_filename = os.path.basename(self.script_path)
        self.script_dir = os.path.dirname(self.script_path)

        if project_name is None:
            self.project_name = os.path.splitext(self.script_filename)[0]
        else:
            self.project_name = project_name

        self.conn = None
        self.run_id = None
        self.flow_id = None
        self.logger = None
        self.log_file_path = None

    def _setup_file_logger(self):
        """Set up file-based logger in the project directory"""
        # Create logs directory
        logs_dir = os.path.join(self.script_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        # Log filename: flow_name_run_ID.log
        log_filename = f"{self.project_name}_run_{self.run_id}.log"
        self.log_file_path = os.path.join(logs_dir, log_filename)

        # Logger configuration
        self.logger = logging.getLogger(f'RunTracker_{self.project_name}_{self.run_id}')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []

        # File handler
        file_handler = logging.FileHandler(self.log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

        # Log run start
        self.logger.info("=" * 80)
        self.logger.info(f"RUN STARTED: {self.project_name}")
        self.logger.info(f"Run ID: {self.run_id}")
        self.logger.info(f"Trigger Type: {self.trigger_type}")
        self.logger.info(f"Script: {self.script_path}")
        self.logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)

    def _cleanup_old_logs_before_new_run(self):
        """Delete old log files before creating a new run"""
        try:
            self.cursor.execute(
                """SELECT run_id, log_file_path, start_time
                   FROM runs 
                   WHERE flow_id = ? AND log_file_path IS NOT NULL
                   ORDER BY start_time DESC""",
                (self.flow_id,)
            )

            all_runs = self.cursor.fetchall()

            if len(all_runs) >= self.max_log_files:
                runs_to_delete = all_runs[self.max_log_files - 1:]

                deleted_count = 0
                for run in runs_to_delete:
                    old_run_id = run[0]
                    old_log_path = run[1]
                    old_start_time = run[2]

                    if old_log_path and os.path.exists(old_log_path):
                        try:
                            os.remove(old_log_path)
                            print(f"[INFO] Old log file deleted: {old_log_path} (Run: {old_start_time})")
                            deleted_count += 1
                        except Exception as e:
                            print(f"[WARNING] Could not delete log file {old_log_path}: {e}")

                    self.cursor.execute(
                        "UPDATE runs SET log_file_path = NULL WHERE run_id = ?",
                        (old_run_id,)
                    )

                if deleted_count > 0:
                    self.conn.commit()
                    print(f"[INFO] {deleted_count} old log files deleted (max: {self.max_log_files})")

        except Exception as e:
            print(f"[ERROR] Error cleaning up old logs: {e}")

    def log(self, message: str, level: str = 'INFO'):
        """
        Write log message to file and console

        Args:
            message: The log message
            level: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        """
        print(f"[{level}] {message}")

        if self.logger:
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            log_method(message)

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        print(f"[INFO] Project/flow: {self.project_name}")
        print(f"[INFO] Script file: {self.script_filename}")

        # Find flow ID
        self.cursor.execute(
            """SELECT flow_id, flow_name, flow_path 
               FROM flows 
               WHERE flow_path LIKE ? AND is_active = 1""",
            (f'%{self.script_filename}',)
        )
        row = self.cursor.fetchone()

        if row is None:
            error_msg = f"No active flow found with script file: '{self.script_filename}'"
            print(f"[ERROR] {error_msg}")
            raise ValueError(error_msg)

        self.flow_id = row["flow_id"]
        print(f"[INFO] Flow found: {row['flow_name']} (ID: {self.flow_id})")

        # Clean up old logs BEFORE creating new run
        self._cleanup_old_logs_before_new_run()

        # Insert new run record with trigger_type
        self.cursor.execute(
            "INSERT INTO runs (flow_id, status, trigger_type) VALUES (?, 'running', ?)",
            (self.flow_id, self.trigger_type)
        )
        self.conn.commit()
        self.run_id = self.cursor.lastrowid

        print(f"[INFO] Run ID: {self.run_id}")

        # Now we have run_id, create the logger
        self._setup_file_logger()
        self.log(f"Run ID: {self.run_id}")

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        finish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if exc_type is None:
            status = 'success'
            error_message = None
            self.log("=" * 80, 'INFO')
            self.log("RUN ENDED SUCCESSFULLY", 'INFO')
            self.log("=" * 80, 'INFO')
        else:
            status = 'fail'
            error_message = f"{str(exc_value)}\n{traceback.format_exc()}"
            self.log("=" * 80, 'ERROR')
            self.log("RUN FAILED", 'ERROR')
            self.log(f"Error: {str(exc_value)}", 'ERROR')
            self.log("=" * 80, 'ERROR')
            self.log("Traceback:", 'ERROR')
            self.log(traceback.format_exc(), 'ERROR')

        # Update run record
        self.cursor.execute(
            "UPDATE runs SET status = ?, finish_time = ?, error_message = ?, log_file_path = ? WHERE run_id = ?",
            (status, finish_time, error_message, self.log_file_path, self.run_id)
        )
        self.conn.commit()
        self.conn.close()

        # Close logger
        if self.logger:
            for handler in self.logger.handlers:
                handler.close()
                self.logger.removeHandler(handler)

        print(f"[INFO] Log file saved: {self.log_file_path}")

        return False