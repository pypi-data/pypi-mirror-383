# Copyright The KiCad Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from google.protobuf.any_pb2 import Any
from google.protobuf.message import Message, DecodeError

from kipy.proto.board import board_types_pb2
from kipy.proto.common.types import base_types_pb2

def pack_any(object: Message) -> Any:
    a = Any()
    a.Pack(object)
    return a

_any_urls = {
    "type.googleapis.com/kiapi.common.types.GraphicShape": base_types_pb2.GraphicShape,

    "type.googleapis.com/kiapi.board.types.Track": board_types_pb2.Track,
    "type.googleapis.com/kiapi.board.types.Arc": board_types_pb2.Arc,
    "type.googleapis.com/kiapi.board.types.Via": board_types_pb2.Via,
    "type.googleapis.com/kiapi.board.types.BoardText": board_types_pb2.BoardText,
    "type.googleapis.com/kiapi.board.types.BoardTextBox": board_types_pb2.BoardTextBox,
    "type.googleapis.com/kiapi.board.types.BoardGraphicShape": board_types_pb2.BoardGraphicShape,
    "type.googleapis.com/kiapi.board.types.Pad": board_types_pb2.Pad,
    "type.googleapis.com/kiapi.board.types.Zone": board_types_pb2.Zone,
    "type.googleapis.com/kiapi.board.types.Dimension": board_types_pb2.Dimension,
    "type.googleapis.com/kiapi.board.types.ReferenceImage": board_types_pb2.ReferenceImage,
    "type.googleapis.com/kiapi.board.types.Group": board_types_pb2.Group,
    "type.googleapis.com/kiapi.board.types.Field": board_types_pb2.Field,
    "type.googleapis.com/kiapi.board.types.FootprintInstance": board_types_pb2.FootprintInstance,
    "type.googleapis.com/kiapi.board.types.Footprint3DModel": board_types_pb2.Footprint3DModel
}

def unpack_any(object: Any) -> Message:
    if len(object.type_url) == 0:
        raise ValueError("Can't unpack empty Any protobuf message")

    type = _any_urls.get(object.type_url, None)
    if type is None:
        raise NotImplementedError(f"Missing type mapping for {object.type_url}, can't unpack it")

    concrete = type()
    try:
        object.Unpack(concrete)
    except DecodeError:
        raise ValueError(f"Can't unpack {object.type_url}.  Incompatible change on KiCad side?") from None
    return concrete
