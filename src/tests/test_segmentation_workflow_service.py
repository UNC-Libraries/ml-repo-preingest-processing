import pytest
from src.utils.segmentation_workflow_service import SegmentationWorkflowService
from src.systems.color_bar_segmentation_system import ColorBarSegmentationSystem
from src.utils.classifier_config import ClassifierConfig
from pathlib import Path
import torch
import csv
from unittest.mock import patch, Mock

@pytest.fixture
def config(tmp_path):
  conf = ClassifierConfig()
  conf.output_base_path = tmp_path / 'output'
  conf.output_base_path.mkdir()
  conf.progress_log_path = tmp_path / 'progress.log'
  conf.predict_rounding_threshold = 0.5
  conf.max_dimension = 512
  conf.min_dimension = 512
  return conf

@pytest.fixture
def mock_model():
    model_mock = Mock()
    value1 = [{
        'boxes': torch.tensor([[  0.0000,  12.5813, 311.6305, 102.0008],
                              [  0.0000,  39.3859, 512.0000,  89.8167],
                              [  0.0000,   6.4033, 512.0000, 119.0521]]),
        'labels': torch.tensor([1, 1, 1]),
        'scores': torch.tensor([0.8920, 0.0657, 0.0568])
      }]
    value2 = [{
        'boxes': torch.zeros((0, 4), dtype=torch.float32),
        'labels': torch.tensor([], dtype=torch.int64),
        'scores': torch.tensor([], dtype=torch.float32)}]
    # each call to model(image) will return a different set of outputs
    model_mock.side_effect = [value1, value2]
    return model_mock

@pytest.fixture
def mock_load_from_checkpoint(mock_model):
  with patch('src.systems.color_bar_segmentation_system.ColorBarSegmentationSystem.load_from_checkpoint') as mock_load:
    mock_load.return_value = mock_model
    yield mock_load

class TestSegmentationWorkflowService:
  def test_process(self, config, tmp_path, mock_load_from_checkpoint):
    report_path = tmp_path / 'report.csv'
    service = SegmentationWorkflowService(config, report_path)
    service.process([Path('./fixtures/normalized_images/gilmer/00276_op0204_0001.jpg'),
      Path('./fixtures/normalized_images/gilmer/00276_op0204_0001_tiny.jpg')])

    assert report_path.exists()
    with open(report_path, newline='') as f:
      reader = csv.reader(f)
      data = list(reader)
      
      assert len(data) == 3
      assert data[1][0] == 'fixtures/normalized_images/gilmer/00276_op0204_0001.jpg'
      assert 'output/00276_op0204_0001.jpg' in data[1][1]
      assert data[1][2] == '1'
      assert data[1][3] == '0.8920'
      assert data[1][4] == '[0.0, 0.0, 809.693359375, 254.203125]'
      assert data[1][5] == '[0.0, 0.0, 324.36328125, 102.0]'

      assert data[2][0] == 'fixtures/normalized_images/gilmer/00276_op0204_0001_tiny.jpg'
      assert 'output/00276_op0204_0001_tiny.jpg' in data[2][1]
      assert data[2][2] == '0'
      assert data[2][3] == '0.0000'
      assert data[2][4] == ''
      assert data[2][5] == ''