import csv, mmengine, io, json, yaml, torch, cv2, os, subprocess, pickle, tqdm
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from torchvision import transforms
from dsdl.dataset import DSDLDataset, DSDLConcatDataset
from mmeval import MeanIoU

def get_gt_masks(data):
    """
    input: single data in dataset, such as {"Image": xxx, "Polygon": xxx}
    output: masks array, shaped as (N, H, W), N means instance nums.
    """
    if "InstanceMap" in data.keys():
        img = data.Image
        single_mask = data.InstanceMap
        
        pix_values = np.unique(single_mask)
        masks = np.zeros((len(pix_values)-1, single_mask.shape[0], single_mask.shape[1]))
        for index, pix in enumerate(pix_values[1:]):
            masks[index-1][single_mask==pix] = 1

    elif "Polygon" in data.keys():
        img = data.Image
        masks = np.zeros((len(data.Polygon), data.Image.shape[0], data.Image.shape[1]))
        idx = 0
        for P in data.Polygon:
            m = P.to_mask(imsize=data.Image.shape[0:2])
            if m.sum() > 0:
                masks[idx] = m
                idx += 1
        masks = masks[0: idx, :, :]

    elif "LabelMap" in data.keys():
        img = data.Image
        single_mask = data.LabelMap
        
        pix_values = np.unique(single_mask)
        masks = np.zeros((len(pix_values)-1, single_mask.shape[0], single_mask.shape[1]))
        for index, pix in enumerate(pix_values[1:]):
            masks[index-1][single_mask==pix] = 1
            
    else:
        print("sample have no mask info !")
        raise
        
    return masks.astype(np.int32)

    
def get_mask_center(mask, use_area=False):
    """
    input: np.array shape as (H, W);
    return: list of int, such as [x, y]
    """
    if use_area:
        coords=np.where(mask == 1)
        x, y = coords[1].mean(), coords[0].mean()
        return [int(x), int(y)]
    else:
        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        M = cv2.moments(contours[-1])
        if M['m00'] == 0:
            M['m00'] += 10**-8
        return [int(M['m10']/M['m00']), int(M['m01']/M['m00'])]


def mask_iou(det_mask, pred_mask):
    '''
    Computes IoU between two masks
    Input: two 2D array mask
    '''
    Union = (pred_mask + det_mask) != 0
    Intersection =  (pred_mask * det_mask) != 0
    return np.sum(Intersection) / np.sum(Union)


def batch_pred_with_point_sampling(predictor, image, masks, points, pred_type="default"):
    assert pred_type in ["default", "oracle"]
    
    if len(image.shape) == 2:                # 单通道
        img = image[..., np.newaxis]
        img = np.repeat(img, 3, axis=-1)
        predictor.set_image(img)
    elif len(image.shape) == 3:    
        if image.shape[-1] == 3:             # 正常三图片
            predictor.set_image(image)
        else:                                # 多通道图片，取前三个通道
            predictor.set_image(image[:, :, 0:3])
        
    else:
        print(f"unsupport image with shape as {image.shape} !")
        return [], []
    
    point_coords = torch.tensor([
        np.array([P])
        for P in points
    ], device=predictor.device)

    point_labels = torch.tensor([
        np.array([1])
        for P in points
    ], device=predictor.device)
    
    transformed_points = predictor.transform.apply_coords_torch(point_coords, image.shape[:2])
    preds, _, _ = predictor.predict_torch(
        point_coords=transformed_points,
        point_labels=point_labels,
        boxes=None,
        multimask_output=False,
    )
    
    pred_masks = []
    ious = []
    for idx in range(len(masks)):
        pred = preds[idx].cpu().numpy()
        if pred_type=="oracle":
            max_mask_id = 0
            max_iou = 0
            for midx in range(3):
                iou = mask_iou(masks[idx], pred[midx])
                if iou > max_iou:
                    max_iou = iou
                    max_mask_id = midx
            pred_masks.append(pred[max_mask_id])
            ious.append(max_iou)
        else:
            pred_masks.append(pred[0])
            ious.append(mask_iou(masks[idx], pred[0]))
    return pred_masks, ious


import sys
sys.path.append("..")
from segment_anything import sam_model_registry, SamPredictor

sam_checkpoint = "../sam_vit_h_4b8939.pth"
model_type = "vit_h"

device = "cuda:0"

print("loading model...")
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

predictor = SamPredictor(sam)


def load_dataset(**args):
    fields_list = ["Image", "LabelMap", "InstanceMap", "Polygon"]
    
    split = args["split"]
    yaml_path = os.path.join(args["dsdl_dir"], f"set-{split}/{split}.yaml")
    
    loc_config = dict(
        type="PetrelFileReader",
        working_dir=args["working_dir"],
        conf_path=args["petrel_cfg"]
    )

    ds = DSDLDataset(dsdl_yaml=yaml_path, location_config=loc_config, required_fields=fields_list)
    ds.data_list = ds.data_list[0:args["sample_nums"]]
    return ds


with open("data_cfgs.json", "r") as f:
    cfgs = json.load(f)["cfgs"]
    
all_dataset = []

print("loading datasets...")
for item in cfgs[0:4]:
    all_dataset.append(load_dataset(**item))
    
    
print("evaluating..., dataset num:", len(all_dataset))

eval_results = []

for ds in all_dataset:
    
    T = {
        "Image": lambda x: x[0].to_array(),
        "LabelMap": lambda x: x[0].to_array(),
        "InstanceMap": lambda x: x[0].to_array(),
        "Polygon": lambda x: x,
    }

    ds.set_transform(T)
    iou_sum = 0
    mask_nums = 0
    
    for data in tqdm.tqdm(ds):
        if "LabelMap" not in data.keys() and "InstanceMap" not in data.keys() and "Polygon" not in data.keys():
            continue
        masks = get_gt_masks(data)
        points = [get_mask_center(masks[i]) for i in range(masks.shape[0])]
        if len(masks) > 0:
            pred_masks, ious = batch_pred_with_point_sampling(predictor, data.Image, masks, points, pred_type="default")
            iou_sum += sum(ious)
            mask_nums += len(ious)
        

    print("==> dataset name:", ds._dsdl_yaml.split('/')[1])
    print("        mask nums:", mask_nums)
    print("        mIoU:", round(iou_sum/mask_nums, 3))
    
    eval_results.append({
        "dataset name":ds._dsdl_yaml.split('/')[1],
        "mask nums": mask_nums,
        "mIoU": round(iou_sum/mask_nums, 3)
    })
    
with open(r"temp.pkl", "wb") as f:   
    pickle.dump(eval_results, f) 