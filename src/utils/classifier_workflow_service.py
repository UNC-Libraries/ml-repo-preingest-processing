import csv
import os
from pathlib import Path
from src.utils.image_classifier import ImageClassifier
from src.utils.image_normalizer import ImageNormalizer
from src.utils.progress_tracker import ProgressTracker

# Service which accepts a list of image original files, then uses normalized versions of 
# those files to use a classifier to make predictions about those images.
# The outcome is written to a CSV file at the provided report_path.
class ClassifierWorkflowService:
  CSV_HEADERS = ['original_path', 'normalized_path', 'predicted_class', 'predicted_conf']

  def __init__(self, config, report_path, restart = False):
    self.config = config
    self.report_path = report_path
    self.normalizer = ImageNormalizer(config)
    self.classifier = ImageClassifier(config)
    self.progress_tracker = ProgressTracker(config.progress_log_path)
    if restart:
      print(f'Restarting progress tracking and reporting')
      self.progress_tracker.reset_log()
      self.report_path.unlink()

  def process(self, paths):
    total = len(paths)
    is_new_file = not Path.exists(self.report_path) or os.path.getsize(self.report_path) == 0

    with open(self.report_path, "a", newline="") as csv_file:
      csv_writer = csv.writer(csv_file)
      # Add headers to file if it is empty
      if is_new_file:
        csv_writer.writerow(self.CSV_HEADERS)

      for idx, path in enumerate(paths):
        if self.progress_tracker.is_complete(path):
          print(f"Skipping {idx + 1} of {total}: {path}")
          continue

        print(f"Processing {idx + 1} of {total}: {path}")
        try:
          normalized_path = self.normalizer.process(path)
          results = self.classifier.predict(normalized_path)
          csv_writer.writerow([path, normalized_path, results[1][0].item(), "{:.4f}".format(results[0][0].item())])
          self.progress_tracker.record_completed(path)
        except (KeyboardInterrupt, SystemExit) as e:
          exit(1)
        except BaseException as e:
          print(f'Failed to process {path}: {e}')
