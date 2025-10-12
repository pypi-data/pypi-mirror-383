import numpy as np

class BinaryParser:
    def __init__(self): ...

class IElementReader:
    def read(self, bparser: BinaryParser): ...
    def data(self): ...

class UInt8Reader(IElementReader):
    def __init__(self, name: str) -> None: ...

class UInt16Reader(IElementReader):
    def __init__(self, name: str) -> None: ...

class UInt32Reader(IElementReader):
    def __init__(self, name: str) -> None: ...

class UInt64Reader(IElementReader):
    def __init__(self, name: str) -> None: ...

class Int8Reader(IElementReader):
    def __init__(self, name: str) -> None: ...

class Int16Reader(IElementReader):
    def __init__(self, name: str) -> None: ...

class Int32Reader(IElementReader):
    def __init__(self, name: str) -> None: ...

class Int64Reader(IElementReader):
    def __init__(self, name: str) -> None: ...

class BoolReader(IElementReader):
    def __init__(self, name: str) -> None: ...

class DoubleReader(IElementReader):
    def __init__(self, name: str) -> None: ...

class FloatReader(IElementReader):
    def __init__(self, name: str) -> None: ...

class STLSeqReader(IElementReader):
    def __init__(
        self,
        name: str,
        with_header: bool,
        objwise_or_memberwise: int,
        element_reader: IElementReader,
    ) -> None: ...

class STLMapReader(IElementReader):
    def __init__(
        self,
        name: str,
        with_header: bool,
        objwise_or_memberwise: int,
        key_reader: IElementReader,
        value_reader: IElementReader,
    ) -> None: ...

class STLStringReader(IElementReader):
    def __init__(
        self,
        name: str,
        with_header: bool,
    ) -> None: ...

class TArrayCReader(IElementReader):
    def __init__(self, name: str) -> None: ...

class TArraySReader(IElementReader):
    def __init__(self, name: str) -> None: ...

class TArrayIReader(IElementReader):
    def __init__(self, name: str) -> None: ...

class TArrayLReader(IElementReader):
    def __init__(self, name: str) -> None: ...

class TArrayFReader(IElementReader):
    def __init__(self, name: str) -> None: ...

class TArrayDReader(IElementReader):
    def __init__(self, name: str) -> None: ...

class TStringReader(IElementReader):
    def __init__(self, name: str) -> None: ...

class TObjectReader(IElementReader):
    def __init__(self, name: str) -> None: ...

class GroupReader(IElementReader):
    def __init__(
        self,
        name: str,
        sub_readers: list[IElementReader],
    ) -> None: ...

class AnyClassReader(IElementReader):
    def __init__(
        self,
        name: str,
        sub_readers: list[IElementReader],
    ) -> None: ...

class ObjectHeaderReader(IElementReader):
    def __init__(
        self,
        name: str,
        element_reader: IElementReader,
    ) -> None: ...

class CStyleArrayReader(IElementReader):
    def __init__(
        self,
        name: str,
        is_obj: bool,
        flat_size: int,
        element_reader: IElementReader,
    ) -> None: ...

class EmptyReader(IElementReader):
    def __init__(self, name: str) -> None: ...

def read_data(data: np.ndarray, offsets: np.ndarray, reader: IElementReader): ...
