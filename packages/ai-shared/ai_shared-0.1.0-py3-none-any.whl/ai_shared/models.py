from pydantic import BaseModel
from pydantic import Field
import numpy as np
from ultralytics.engine.results import Results


class InferenceMeta(BaseModel):
    model_name: str
    image_path: str | None
    image_width: int
    image_height: int


class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    width: float
    height: float


class Detection(BaseModel):
    bbox: BBox
    confidence: float
    class_id: int
    class_name: str | None
    track_id: int | None


class Keypoint(BaseModel):
    x: float
    y: float
    confidence: float | None


class KeypointsSet(BaseModel):
    points: list[Keypoint]


class SegmentationMask(BaseModel):
    # 简化：只存 RLE 或二值矩阵的路径/尺寸；若需要完整数据可改为 ndarray -> base64
    height: int
    width: int
    # 可选：掩码像素点索引（True 的位置），用于存储分割掩码中为 True 的像素点的线性索引（按 numpy.flatnonzero 方式），
    # 当掩码较大时可设为 None 以避免占用过多内存，后续可用于重建掩码或分析分割区域。
    indices: list[int] | None


class Classification(BaseModel):
    class_id: int
    class_name: str | None
    confidence: float


class InferenceOutput(BaseModel):
    meta: InferenceMeta
    detections: list[Detection] = Field(default_factory=list)
    keypoints: list[KeypointsSet] = Field(default_factory=list)
    masks: list[SegmentationMask] = Field(default_factory=list)
    classifications: list[Classification] = Field(default_factory=list)


def parse_ultralytics_result(
    result: Results,
    model_name: str,
    image_path: str | None = None,
    class_names: list[str] | None = None,
) -> InferenceOutput:
    """
    将单个 Ultralytics result 转换为结构化 Pydantic 对象。

    Args:
        result (ultralytics.engine.results.Results): Ultralytics 推理结果对象。
        model_name (str): 模型名称。
        image_path (str | None, optional): 输入图片路径。
        class_names (list[str] | None, optional): 类别名称列表。

    Returns:
        InferenceOutput: 结构化推理输出对象。
    """
    h, w = result.orig_shape  # (height, width)
    out = InferenceOutput(
        meta=InferenceMeta(
            model_name=model_name,
            image_path=image_path,
            image_width=w,
            image_height=h,
        )
    )

    # 检测框
    if getattr(result, "boxes", None) is not None and result.boxes is not None:
        boxes = result.boxes
        # xyxy: (N,4)
        xyxy = boxes.xyxy.cpu().numpy()
        confs = (
            boxes.conf.cpu().numpy() if boxes.conf is not None else np.ones(len(xyxy))
        )
        clses = (
            boxes.cls.cpu().numpy().astype(int)
            if boxes.cls is not None
            else np.zeros(len(xyxy), dtype=int)
        )
        ids = (
            boxes.id.cpu().numpy().astype(int)
            if boxes.id is not None
            else [None] * len(xyxy)
        )

        for i, (x1, y1, x2, y2) in enumerate(xyxy):
            w_box = x2 - x1
            h_box = y2 - y1
            cls_id = int(clses[i])
            out.detections.append(
                Detection(
                    bbox=BBox(
                        x1=float(x1),
                        y1=float(y1),
                        x2=float(x2),
                        y2=float(y2),
                        width=float(w_box),
                        height=float(h_box),
                    ),
                    confidence=float(confs[i]),
                    class_id=cls_id,
                    class_name=(
                        class_names[cls_id]
                        if class_names and cls_id < len(class_names)
                        else None
                    ),
                    track_id=int(ids[i]) if ids[i] is not None else None,
                )
            )

    # 关键点（姿态）
    if getattr(result, "keypoints", None) is not None and result.keypoints is not None:
        kpts = result.keypoints  # shape (N,K,2或3)
        arr = kpts.data.cpu().numpy()
        # 若包含 (x,y,conf)
        for person in arr:
            pts = []
            for kp in person:
                if len(kp) == 3:
                    x, y, c = kp
                    pts.append(Keypoint(x=float(x), y=float(y), confidence=float(c)))
                else:
                    x, y = kp
                    pts.append(Keypoint(x=float(x), y=float(y)))
            out.keypoints.append(KeypointsSet(points=pts))

    # 分割掩码
    if getattr(result, "masks", None) is not None and result.masks is not None:
        masks = result.masks.data  # (N,H,W)
        # 优化：一次性转为 numpy，避免循环内多次转换
        masks_np = masks.cpu().numpy()  # (N,H,W)
        for m in masks_np:
            # 只存 True 像素索引（可选，较小但仍可能很大）
            bin_mask = m > 0.5
            indices = np.flatnonzero(bin_mask).tolist()
            out.masks.append(
                SegmentationMask(
                    height=bin_mask.shape[0],
                    width=bin_mask.shape[1],
                    indices=indices if len(indices) < 50000 else None,  # 避免过大
                )
            )

    # 分类（若是分类模型）
    if getattr(result, "probs", None) is not None and result.probs is not None:
        probs = result.probs.data.cpu().numpy()  # (num_classes,)
        top_idx = int(np.argmax(probs))
        out.classifications.append(
            Classification(
                class_id=top_idx,
                class_name=(
                    class_names[top_idx]
                    if class_names and top_idx < len(class_names)
                    else None
                ),
                confidence=float(probs[top_idx]),
            )
        )

    return out
