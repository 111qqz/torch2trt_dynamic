from torch2trt.torch2trt import *

from torch2trt.plugins import *
import mmdet


@tensorrt_converter('mmdet.models.roi_extractors.SingleRoIExtractor.forward')
def convert_roiextractor(ctx):
    module = ctx.method_args[0]
    feats = get_arg(ctx, 'feats', pos=1, default=None)
    rois = get_arg(ctx, 'rois', pos=2, default=None)
    roi_scale_factor = get_arg(ctx, 'roi_scale_factor', pos=3, default=None)
    
    out_size = module.roi_layers[0].out_size[0]
    sample_num = module.roi_layers[0].sample_num
    featmap_strides = module.featmap_strides
    finest_scale = module.finest_scale

    feats_trt = [trt_(ctx.network, f) for f in feats]
    rois_trt = trt_(ctx.network, rois)
    output = ctx.method_return

    plugin = create_roiextractor_plugin("roiextractor_" + str(id(module)),
                                       out_size,
                                       sample_num,
                                       featmap_strides,
                                       roi_scale_factor,
                                       finest_scale)
                                       
    custom_layer = ctx.network.add_plugin_v2(
        inputs=[rois_trt] + feats_trt, plugin=plugin)

    output._trt = custom_layer.get_output(0)
