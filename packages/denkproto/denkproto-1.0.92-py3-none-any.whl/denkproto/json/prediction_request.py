from uuid import UUID
from typing import Any, Dict, List, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_dict(f: Callable[[Any], T], x: Any) -> Dict[str, T]:
    assert isinstance(x, dict)
    return { k: f(v) for (k, v) in x.items() }


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


class Image:
    blob_id: UUID
    height: int
    owned_by_group_id: UUID
    width: int

    def __init__(self, blob_id: UUID, height: int, owned_by_group_id: UUID, width: int) -> None:
        self.blob_id = blob_id
        self.height = height
        self.owned_by_group_id = owned_by_group_id
        self.width = width

    @staticmethod
    def from_dict(obj: Any) -> 'Image':
        assert isinstance(obj, dict)
        blob_id = UUID(obj.get("blob_id"))
        height = from_int(obj.get("height"))
        owned_by_group_id = UUID(obj.get("owned_by_group_id"))
        width = from_int(obj.get("width"))
        return Image(blob_id, height, owned_by_group_id, width)

    def to_dict(self) -> dict:
        result: dict = {}
        result["blob_id"] = str(self.blob_id)
        result["height"] = from_int(self.height)
        result["owned_by_group_id"] = str(self.owned_by_group_id)
        result["width"] = from_int(self.width)
        return result


class ClassLabel:
    id: UUID
    idx: int

    def __init__(self, id: UUID, idx: int) -> None:
        self.id = id
        self.idx = idx

    @staticmethod
    def from_dict(obj: Any) -> 'ClassLabel':
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        idx = from_int(obj.get("idx"))
        return ClassLabel(id, idx)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id)
        result["idx"] = from_int(self.idx)
        return result


class Config:
    metadata: Dict[str, Any]
    uses_validation_tiling: bool

    def __init__(self, metadata: Dict[str, Any], uses_validation_tiling: bool) -> None:
        self.metadata = metadata
        self.uses_validation_tiling = uses_validation_tiling

    @staticmethod
    def from_dict(obj: Any) -> 'Config':
        assert isinstance(obj, dict)
        metadata = from_dict(lambda x: x, obj.get("metadata"))
        uses_validation_tiling = from_bool(obj.get("uses_validation_tiling"))
        return Config(metadata, uses_validation_tiling)

    def to_dict(self) -> dict:
        result: dict = {}
        result["metadata"] = from_dict(lambda x: x, self.metadata)
        result["uses_validation_tiling"] = from_bool(self.uses_validation_tiling)
        return result


class Onnx:
    blob_id: UUID
    owned_by_group_id: UUID

    def __init__(self, blob_id: UUID, owned_by_group_id: UUID) -> None:
        self.blob_id = blob_id
        self.owned_by_group_id = owned_by_group_id

    @staticmethod
    def from_dict(obj: Any) -> 'Onnx':
        assert isinstance(obj, dict)
        blob_id = UUID(obj.get("blob_id"))
        owned_by_group_id = UUID(obj.get("owned_by_group_id"))
        return Onnx(blob_id, owned_by_group_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["blob_id"] = str(self.blob_id)
        result["owned_by_group_id"] = str(self.owned_by_group_id)
        return result


class Pytorch:
    blob_id: UUID
    owned_by_group_id: UUID

    def __init__(self, blob_id: UUID, owned_by_group_id: UUID) -> None:
        self.blob_id = blob_id
        self.owned_by_group_id = owned_by_group_id

    @staticmethod
    def from_dict(obj: Any) -> 'Pytorch':
        assert isinstance(obj, dict)
        blob_id = UUID(obj.get("blob_id"))
        owned_by_group_id = UUID(obj.get("owned_by_group_id"))
        return Pytorch(blob_id, owned_by_group_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["blob_id"] = str(self.blob_id)
        result["owned_by_group_id"] = str(self.owned_by_group_id)
        return result


class Snapshot:
    onnx: Onnx
    pytorch: Pytorch

    def __init__(self, onnx: Onnx, pytorch: Pytorch) -> None:
        self.onnx = onnx
        self.pytorch = pytorch

    @staticmethod
    def from_dict(obj: Any) -> 'Snapshot':
        assert isinstance(obj, dict)
        onnx = Onnx.from_dict(obj.get("onnx"))
        pytorch = Pytorch.from_dict(obj.get("pytorch"))
        return Snapshot(onnx, pytorch)

    def to_dict(self) -> dict:
        result: dict = {}
        result["onnx"] = to_class(Onnx, self.onnx)
        result["pytorch"] = to_class(Pytorch, self.pytorch)
        return result


class NetworkExperiment:
    class_labels: List[ClassLabel]
    config: Config
    flavor: str
    network_typename: str
    snapshot: Snapshot

    def __init__(self, class_labels: List[ClassLabel], config: Config, flavor: str, network_typename: str, snapshot: Snapshot) -> None:
        self.class_labels = class_labels
        self.config = config
        self.flavor = flavor
        self.network_typename = network_typename
        self.snapshot = snapshot

    @staticmethod
    def from_dict(obj: Any) -> 'NetworkExperiment':
        assert isinstance(obj, dict)
        class_labels = from_list(ClassLabel.from_dict, obj.get("class_labels"))
        config = Config.from_dict(obj.get("config"))
        flavor = from_str(obj.get("flavor"))
        network_typename = from_str(obj.get("network_typename"))
        snapshot = Snapshot.from_dict(obj.get("snapshot"))
        return NetworkExperiment(class_labels, config, flavor, network_typename, snapshot)

    def to_dict(self) -> dict:
        result: dict = {}
        result["class_labels"] = from_list(lambda x: to_class(ClassLabel, x), self.class_labels)
        result["config"] = to_class(Config, self.config)
        result["flavor"] = from_str(self.flavor)
        result["network_typename"] = from_str(self.network_typename)
        result["snapshot"] = to_class(Snapshot, self.snapshot)
        return result


class PredictionRequest:
    created_by_user_id: UUID
    id: UUID
    image: Image
    network_experiment: NetworkExperiment
    owned_by_group_id: UUID
    prediction_priority: int
    request_classification_interpretation: bool

    def __init__(self, created_by_user_id: UUID, id: UUID, image: Image, network_experiment: NetworkExperiment, owned_by_group_id: UUID, prediction_priority: int, request_classification_interpretation: bool) -> None:
        self.created_by_user_id = created_by_user_id
        self.id = id
        self.image = image
        self.network_experiment = network_experiment
        self.owned_by_group_id = owned_by_group_id
        self.prediction_priority = prediction_priority
        self.request_classification_interpretation = request_classification_interpretation

    @staticmethod
    def from_dict(obj: Any) -> 'PredictionRequest':
        assert isinstance(obj, dict)
        created_by_user_id = UUID(obj.get("created_by_user_id"))
        id = UUID(obj.get("id"))
        image = Image.from_dict(obj.get("image"))
        network_experiment = NetworkExperiment.from_dict(obj.get("network_experiment"))
        owned_by_group_id = UUID(obj.get("owned_by_group_id"))
        prediction_priority = from_int(obj.get("prediction_priority"))
        request_classification_interpretation = from_bool(obj.get("request_classification_interpretation"))
        return PredictionRequest(created_by_user_id, id, image, network_experiment, owned_by_group_id, prediction_priority, request_classification_interpretation)

    def to_dict(self) -> dict:
        result: dict = {}
        result["created_by_user_id"] = str(self.created_by_user_id)
        result["id"] = str(self.id)
        result["image"] = to_class(Image, self.image)
        result["network_experiment"] = to_class(NetworkExperiment, self.network_experiment)
        result["owned_by_group_id"] = str(self.owned_by_group_id)
        result["prediction_priority"] = from_int(self.prediction_priority)
        result["request_classification_interpretation"] = from_bool(self.request_classification_interpretation)
        return result


def prediction_request_from_dict(s: Any) -> PredictionRequest:
    return PredictionRequest.from_dict(s)


def prediction_request_to_dict(x: PredictionRequest) -> Any:
    return to_class(PredictionRequest, x)
