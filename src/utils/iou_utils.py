from torchvision.ops import box_iou, generalized_box_iou
import torch

_all__ = ["_evaluate_iou", "_evaluate_giou"]

def evaluate_iou(target, pred):
    """
    Evaluate intersection over union (IOU) for target from dataset and output prediction
    from model.
    """
    # If there is no target or predicted bounding box, then we have total match
    if pred.shape[0] == 0 and target.shape[0] == 0:
        return torch.tensor(1.0, device=pred.device)
    # If only one is empty, then we have no matching
    if pred.shape[0] == 0 or target.shape[0] == 0:
        return torch.tensor(0.0, device=pred.device)
    # return box_iou(target["boxes"], pred["boxes"]).diag().mean()
    return box_iou(target.unsqueeze(0), pred.unsqueeze(0)).diag().mean()


def evaluate_giou(target, pred):
    """
    Evaluate generalized intersection over union (gIOU) for target from dataset and output prediction
    from model.
    """

    # If there is no target or predicted bounding box, then we have total match
    if pred.shape[0] == 0 and target.shape[0] == 0:
        return torch.tensor(1.0, device=pred.device)
    # If only one is empty, then we have no matching
    if pred.shape[0] == 0 or target.shape[0] == 0:
        return torch.tensor(0.0, device=pred.device)
    # return generalized_box_iou(target["boxes"], pred["boxes"]).diag().mean()
    return generalized_box_iou(target.unsqueeze(0), pred.unsqueeze(0)).diag().mean()
