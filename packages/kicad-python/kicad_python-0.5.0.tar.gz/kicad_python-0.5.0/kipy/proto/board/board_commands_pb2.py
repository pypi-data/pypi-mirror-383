"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 1, '', 'board/board_commands.proto')
_sym_db = _symbol_database.Default()
from ..common.types import base_types_pb2 as common_dot_types_dot_base__types__pb2
from ..common.types import enums_pb2 as common_dot_types_dot_enums__pb2
from ..common.types import project_settings_pb2 as common_dot_types_dot_project__settings__pb2
from ..board import board_pb2 as board_dot_board__pb2
from ..board import board_types_pb2 as board_dot_board__types__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1aboard/board_commands.proto\x12\x14kiapi.board.commands\x1a\x1dcommon/types/base_types.proto\x1a\x18common/types/enums.proto\x1a#common/types/project_settings.proto\x1a\x11board/board.proto\x1a\x17board/board_types.proto"G\n\x0fGetBoardStackup\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier"B\n\x14BoardStackupResponse\x12*\n\x07stackup\x18\x01 \x01(\x0b2\x19.kiapi.board.BoardStackup"v\n\x12UpdateBoardStackup\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x12*\n\x07stackup\x18\x02 \x01(\x0b2\x19.kiapi.board.BoardStackup"M\n\x15GetBoardEnabledLayers\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier"g\n\x1aBoardEnabledLayersResponse\x12\x1a\n\x12copper_layer_count\x18\x01 \x01(\r\x12-\n\x06layers\x18\x02 \x03(\x0e2\x1d.kiapi.board.types.BoardLayer"\x98\x01\n\x15SetBoardEnabledLayers\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x12\x1a\n\x12copper_layer_count\x18\x02 \x01(\r\x12-\n\x06layers\x18\x03 \x03(\x0e2\x1d.kiapi.board.types.BoardLayer"K\n\x13GetGraphicsDefaults\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier"K\n\x18GraphicsDefaultsResponse\x12/\n\x08defaults\x18\x01 \x01(\x0b2\x1d.kiapi.board.GraphicsDefaults"{\n\x0eGetBoardOrigin\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x123\n\x04type\x18\x02 \x01(\x0e2%.kiapi.board.commands.BoardOriginType"\xa8\x01\n\x0eSetBoardOrigin\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x123\n\x04type\x18\x02 \x01(\x0e2%.kiapi.board.commands.BoardOriginType\x12+\n\x06origin\x18\x03 \x01(\x0b2\x1b.kiapi.common.types.Vector2"X\n\x07GetNets\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x12\x17\n\x0fnetclass_filter\x18\x02 \x03(\t"4\n\x0cNetsResponse\x12$\n\x04nets\x18\x01 \x03(\x0b2\x16.kiapi.board.types.Net"\xa2\x01\n\rGetItemsByNet\x12.\n\x06header\x18\x01 \x01(\x0b2\x1e.kiapi.common.types.ItemHeader\x122\n\x05types\x18\x02 \x03(\x0e2#.kiapi.common.types.KiCadObjectType\x12-\n\tnet_codes\x18\x03 \x03(\x0b2\x1a.kiapi.board.types.NetCode"\x8d\x01\n\x12GetItemsByNetClass\x12.\n\x06header\x18\x01 \x01(\x0b2\x1e.kiapi.common.types.ItemHeader\x122\n\x05types\x18\x02 \x03(\x0e2#.kiapi.common.types.KiCadObjectType\x12\x13\n\x0bnet_classes\x18\x03 \x03(\t"9\n\x12GetNetClassForNets\x12#\n\x03net\x18\x01 \x03(\x0b2\x16.kiapi.board.types.Net"\xb6\x01\n\x17NetClassForNetsResponse\x12K\n\x07classes\x18\x01 \x03(\x0b2:.kiapi.board.commands.NetClassForNetsResponse.ClassesEntry\x1aN\n\x0cClassesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12-\n\x05value\x18\x02 \x01(\x0b2\x1e.kiapi.common.project.NetClass:\x028\x01"l\n\x0bRefillZones\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x12\'\n\x05zones\x18\x02 \x03(\x0b2\x18.kiapi.common.types.KIID"\xa2\x01\n\x14GetPadShapeAsPolygon\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x12&\n\x04pads\x18\x02 \x03(\x0b2\x18.kiapi.common.types.KIID\x12,\n\x05layer\x18\x03 \x01(\x0e2\x1d.kiapi.board.types.BoardLayer"{\n\x19PadShapeAsPolygonResponse\x12&\n\x04pads\x18\x01 \x03(\x0b2\x18.kiapi.common.types.KIID\x126\n\x08polygons\x18\x02 \x03(\x0b2$.kiapi.common.types.PolygonWithHoles"\xad\x01\n\x1dCheckPadstackPresenceOnLayers\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x12\'\n\x05items\x18\x02 \x03(\x0b2\x18.kiapi.common.types.KIID\x12-\n\x06layers\x18\x03 \x03(\x0e2\x1d.kiapi.board.types.BoardLayer"\xa7\x01\n\x15PadstackPresenceEntry\x12&\n\x04item\x18\x01 \x01(\x0b2\x18.kiapi.common.types.KIID\x12,\n\x05layer\x18\x02 \x01(\x0e2\x1d.kiapi.board.types.BoardLayer\x128\n\x08presence\x18\x03 \x01(\x0e2&.kiapi.board.commands.PadstackPresence"X\n\x18PadstackPresenceResponse\x12<\n\x07entries\x18\x01 \x03(\x0b2+.kiapi.board.commands.PadstackPresenceEntry"H\n\x10GetVisibleLayers\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier"B\n\x12BoardLayerResponse\x12,\n\x05layer\x18\x01 \x01(\x0e2\x1d.kiapi.board.types.BoardLayer"<\n\x0bBoardLayers\x12-\n\x06layers\x18\x01 \x03(\x0e2\x1d.kiapi.board.types.BoardLayer"w\n\x10SetVisibleLayers\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x12-\n\x06layers\x18\x02 \x03(\x0e2\x1d.kiapi.board.types.BoardLayer"F\n\x0eGetActiveLayer\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier"t\n\x0eSetActiveLayer\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x12,\n\x05layer\x18\x02 \x01(\x0e2\x1d.kiapi.board.types.BoardLayer"\xb3\x02\n\x1dBoardEditorAppearanceSettings\x12N\n\x16inactive_layer_display\x18\x01 \x01(\x0e2..kiapi.board.commands.InactiveLayerDisplayMode\x12D\n\x11net_color_display\x18\x02 \x01(\x0e2).kiapi.board.commands.NetColorDisplayMode\x127\n\nboard_flip\x18\x03 \x01(\x0e2#.kiapi.board.commands.BoardFlipMode\x12C\n\x10ratsnest_display\x18\x04 \x01(\x0e2).kiapi.board.commands.RatsnestDisplayMode""\n GetBoardEditorAppearanceSettings"i\n SetBoardEditorAppearanceSettings\x12E\n\x08settings\x18\x01 \x01(\x0b23.kiapi.board.commands.BoardEditorAppearanceSettings"u\n\x14InteractiveMoveItems\x124\n\x05board\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x12\'\n\x05items\x18\x02 \x03(\x0b2\x18.kiapi.common.types.KIID*?\n\x0fBoardOriginType\x12\x0f\n\x0bBOT_UNKNOWN\x10\x00\x12\x0c\n\x08BOT_GRID\x10\x01\x12\r\n\tBOT_DRILL\x10\x02*I\n\x10PadstackPresence\x12\x0f\n\x0bPSP_UNKNOWN\x10\x00\x12\x0f\n\x0bPSP_PRESENT\x10\x01\x12\x13\n\x0fPSP_NOT_PRESENT\x10\x02*_\n\x18InactiveLayerDisplayMode\x12\x10\n\x0cILDM_UNKNOWN\x10\x00\x12\x0f\n\x0bILDM_NORMAL\x10\x01\x12\x0f\n\x0bILDM_DIMMED\x10\x02\x12\x0f\n\x0bILDM_HIDDEN\x10\x03*V\n\x13NetColorDisplayMode\x12\x10\n\x0cNCDM_UNKNOWN\x10\x00\x12\x0c\n\x08NCDM_ALL\x10\x01\x12\x11\n\rNCDM_RATSNEST\x10\x02\x12\x0c\n\x08NCDM_OFF\x10\x03*C\n\rBoardFlipMode\x12\x0f\n\x0bBFM_UNKNOWN\x10\x00\x12\x0e\n\nBFM_NORMAL\x10\x01\x12\x11\n\rBFM_FLIPPED_X\x10\x02*R\n\x13RatsnestDisplayMode\x12\x0f\n\x0bRDM_UNKNOWN\x10\x00\x12\x12\n\x0eRDM_ALL_LAYERS\x10\x01\x12\x16\n\x12RDM_VISIBLE_LAYERS\x10\x02b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'board.board_commands_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_NETCLASSFORNETSRESPONSE_CLASSESENTRY']._loaded_options = None
    _globals['_NETCLASSFORNETSRESPONSE_CLASSESENTRY']._serialized_options = b'8\x01'
    _globals['_BOARDORIGINTYPE']._serialized_start = 3860
    _globals['_BOARDORIGINTYPE']._serialized_end = 3923
    _globals['_PADSTACKPRESENCE']._serialized_start = 3925
    _globals['_PADSTACKPRESENCE']._serialized_end = 3998
    _globals['_INACTIVELAYERDISPLAYMODE']._serialized_start = 4000
    _globals['_INACTIVELAYERDISPLAYMODE']._serialized_end = 4095
    _globals['_NETCOLORDISPLAYMODE']._serialized_start = 4097
    _globals['_NETCOLORDISPLAYMODE']._serialized_end = 4183
    _globals['_BOARDFLIPMODE']._serialized_start = 4185
    _globals['_BOARDFLIPMODE']._serialized_end = 4252
    _globals['_RATSNESTDISPLAYMODE']._serialized_start = 4254
    _globals['_RATSNESTDISPLAYMODE']._serialized_end = 4336
    _globals['_GETBOARDSTACKUP']._serialized_start = 190
    _globals['_GETBOARDSTACKUP']._serialized_end = 261
    _globals['_BOARDSTACKUPRESPONSE']._serialized_start = 263
    _globals['_BOARDSTACKUPRESPONSE']._serialized_end = 329
    _globals['_UPDATEBOARDSTACKUP']._serialized_start = 331
    _globals['_UPDATEBOARDSTACKUP']._serialized_end = 449
    _globals['_GETBOARDENABLEDLAYERS']._serialized_start = 451
    _globals['_GETBOARDENABLEDLAYERS']._serialized_end = 528
    _globals['_BOARDENABLEDLAYERSRESPONSE']._serialized_start = 530
    _globals['_BOARDENABLEDLAYERSRESPONSE']._serialized_end = 633
    _globals['_SETBOARDENABLEDLAYERS']._serialized_start = 636
    _globals['_SETBOARDENABLEDLAYERS']._serialized_end = 788
    _globals['_GETGRAPHICSDEFAULTS']._serialized_start = 790
    _globals['_GETGRAPHICSDEFAULTS']._serialized_end = 865
    _globals['_GRAPHICSDEFAULTSRESPONSE']._serialized_start = 867
    _globals['_GRAPHICSDEFAULTSRESPONSE']._serialized_end = 942
    _globals['_GETBOARDORIGIN']._serialized_start = 944
    _globals['_GETBOARDORIGIN']._serialized_end = 1067
    _globals['_SETBOARDORIGIN']._serialized_start = 1070
    _globals['_SETBOARDORIGIN']._serialized_end = 1238
    _globals['_GETNETS']._serialized_start = 1240
    _globals['_GETNETS']._serialized_end = 1328
    _globals['_NETSRESPONSE']._serialized_start = 1330
    _globals['_NETSRESPONSE']._serialized_end = 1382
    _globals['_GETITEMSBYNET']._serialized_start = 1385
    _globals['_GETITEMSBYNET']._serialized_end = 1547
    _globals['_GETITEMSBYNETCLASS']._serialized_start = 1550
    _globals['_GETITEMSBYNETCLASS']._serialized_end = 1691
    _globals['_GETNETCLASSFORNETS']._serialized_start = 1693
    _globals['_GETNETCLASSFORNETS']._serialized_end = 1750
    _globals['_NETCLASSFORNETSRESPONSE']._serialized_start = 1753
    _globals['_NETCLASSFORNETSRESPONSE']._serialized_end = 1935
    _globals['_NETCLASSFORNETSRESPONSE_CLASSESENTRY']._serialized_start = 1857
    _globals['_NETCLASSFORNETSRESPONSE_CLASSESENTRY']._serialized_end = 1935
    _globals['_REFILLZONES']._serialized_start = 1937
    _globals['_REFILLZONES']._serialized_end = 2045
    _globals['_GETPADSHAPEASPOLYGON']._serialized_start = 2048
    _globals['_GETPADSHAPEASPOLYGON']._serialized_end = 2210
    _globals['_PADSHAPEASPOLYGONRESPONSE']._serialized_start = 2212
    _globals['_PADSHAPEASPOLYGONRESPONSE']._serialized_end = 2335
    _globals['_CHECKPADSTACKPRESENCEONLAYERS']._serialized_start = 2338
    _globals['_CHECKPADSTACKPRESENCEONLAYERS']._serialized_end = 2511
    _globals['_PADSTACKPRESENCEENTRY']._serialized_start = 2514
    _globals['_PADSTACKPRESENCEENTRY']._serialized_end = 2681
    _globals['_PADSTACKPRESENCERESPONSE']._serialized_start = 2683
    _globals['_PADSTACKPRESENCERESPONSE']._serialized_end = 2771
    _globals['_GETVISIBLELAYERS']._serialized_start = 2773
    _globals['_GETVISIBLELAYERS']._serialized_end = 2845
    _globals['_BOARDLAYERRESPONSE']._serialized_start = 2847
    _globals['_BOARDLAYERRESPONSE']._serialized_end = 2913
    _globals['_BOARDLAYERS']._serialized_start = 2915
    _globals['_BOARDLAYERS']._serialized_end = 2975
    _globals['_SETVISIBLELAYERS']._serialized_start = 2977
    _globals['_SETVISIBLELAYERS']._serialized_end = 3096
    _globals['_GETACTIVELAYER']._serialized_start = 3098
    _globals['_GETACTIVELAYER']._serialized_end = 3168
    _globals['_SETACTIVELAYER']._serialized_start = 3170
    _globals['_SETACTIVELAYER']._serialized_end = 3286
    _globals['_BOARDEDITORAPPEARANCESETTINGS']._serialized_start = 3289
    _globals['_BOARDEDITORAPPEARANCESETTINGS']._serialized_end = 3596
    _globals['_GETBOARDEDITORAPPEARANCESETTINGS']._serialized_start = 3598
    _globals['_GETBOARDEDITORAPPEARANCESETTINGS']._serialized_end = 3632
    _globals['_SETBOARDEDITORAPPEARANCESETTINGS']._serialized_start = 3634
    _globals['_SETBOARDEDITORAPPEARANCESETTINGS']._serialized_end = 3739
    _globals['_INTERACTIVEMOVEITEMS']._serialized_start = 3741
    _globals['_INTERACTIVEMOVEITEMS']._serialized_end = 3858