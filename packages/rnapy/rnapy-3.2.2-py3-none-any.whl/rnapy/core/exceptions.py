class RNAPyError(Exception):
    pass


class ModelError(RNAPyError):
    pass


class ModelNotFoundError(ModelError):
    pass


class ModelLoadError(ModelError):
    pass


class PredictionError(ModelError):
    pass


class ConfigError(RNAPyError):
    pass


class ConfigNotFoundError(ConfigError):
    pass


class DataError(RNAPyError):
    pass


class InvalidSequenceError(DataError):
    pass


class FormatError(DataError):
    pass


class DeviceError(RNAPyError):
    pass 