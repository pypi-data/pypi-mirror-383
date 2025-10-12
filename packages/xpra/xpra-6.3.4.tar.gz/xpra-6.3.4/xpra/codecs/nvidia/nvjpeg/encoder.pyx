# This file is part of Xpra.
# Copyright (C) 2021 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

from time import monotonic
from math import ceil
from typing import Any, Dict, Tuple, List
from collections.abc import Sequence

from libc.stdint cimport uintptr_t
from xpra.codecs.image import ImageWrapper
from xpra.codecs.constants import VideoSpec
from xpra.buffers.membuf cimport getbuf, MemBuf  # pylint: disable=syntax-error
from xpra.codecs.nvidia.nvjpeg.nvjpeg cimport (
    NV_ENC_INPUT_PTR, NV_ENC_OUTPUT_PTR, NV_ENC_REGISTERED_PTR,
    nvjpegStatus_t, nvjpegChromaSubsampling_t, nvjpegOutputFormat_t,
    nvjpegInputFormat_t, nvjpegBackend_t, nvjpegJpegEncoding_t,
    nvjpegImage_t, nvjpegHandle_t,
    nvjpegGetProperty, nvjpegCreateSimple, nvjpegDestroy,
    NVJPEG_ENCODING_BASELINE_DCT, NVJPEG_CSS_GRAY, NVJPEG_INPUT_RGBI, NVJPEG_INPUT_RGB,
    NVJPEG_CSS_444, NVJPEG_CSS_422, NVJPEG_CSS_420,
)
from xpra.codecs.nvidia.nvjpeg.common import (
    get_version,
    errcheck, NVJPEG_Exception,
    CSS_STR, ENCODING_STR, NVJPEG_INPUT_STR,
)
from xpra.codecs.debug import may_save_image
from xpra.codecs.nvidia.cuda.context import get_CUDA_function, select_device, cuda_device_context
from xpra.net.compression import Compressed
from xpra.util.objects import typedict

from xpra.log import Logger
log = Logger("encoder", "nvjpeg")

#we can import pycuda safely here,
#because importing cuda/context will have imported it with the lock
from pycuda import driver  # @UnresolvedImport
from numpy import int32


DEF NVJPEG_MAX_COMPONENT = 4

cdef extern from "cuda_runtime_api.h":
    ctypedef void* cudaStream_t

cdef extern from "nvjpeg.h":
    #Encode specific:
    ctypedef struct nvjpegEncoderState:
        pass
    ctypedef nvjpegEncoderState* nvjpegEncoderState_t

    nvjpegStatus_t nvjpegEncoderStateCreate(
        nvjpegHandle_t handle,
        nvjpegEncoderState_t *encoder_state,
        cudaStream_t stream);
    nvjpegStatus_t nvjpegEncoderStateDestroy(nvjpegEncoderState_t encoder_state)
    ctypedef struct nvjpegEncoderParams:
        pass
    ctypedef nvjpegEncoderParams* nvjpegEncoderParams_t
    nvjpegStatus_t nvjpegEncoderParamsCreate(
        nvjpegHandle_t handle,
        nvjpegEncoderParams_t *encoder_params,
        cudaStream_t stream)
    nvjpegStatus_t nvjpegEncoderParamsDestroy(nvjpegEncoderParams_t encoder_params)
    nvjpegStatus_t nvjpegEncoderParamsSetQuality(
        nvjpegEncoderParams_t encoder_params,
        const int quality,
        cudaStream_t stream)
    nvjpegStatus_t nvjpegEncoderParamsSetEncoding(
        nvjpegEncoderParams_t encoder_params,
        nvjpegJpegEncoding_t etype,
        cudaStream_t stream)
    nvjpegStatus_t nvjpegEncoderParamsSetOptimizedHuffman(
        nvjpegEncoderParams_t encoder_params,
        const int optimized,
        cudaStream_t stream)
    nvjpegStatus_t nvjpegEncoderParamsSetSamplingFactors(
        nvjpegEncoderParams_t encoder_params,
        const nvjpegChromaSubsampling_t chroma_subsampling,
        cudaStream_t stream)
    nvjpegStatus_t nvjpegEncodeGetBufferSize(
        nvjpegHandle_t handle,
        const nvjpegEncoderParams_t encoder_params,
        int image_width,
        int image_height,
        size_t *max_stream_length)
    nvjpegStatus_t nvjpegEncodeYUV(
            nvjpegHandle_t handle,
            nvjpegEncoderState_t encoder_state,
            const nvjpegEncoderParams_t encoder_params,
            const nvjpegImage_t *source,
            nvjpegChromaSubsampling_t chroma_subsampling,
            int image_width,
            int image_height,
            cudaStream_t stream) nogil
    nvjpegStatus_t nvjpegEncodeImage(
            nvjpegHandle_t handle,
            nvjpegEncoderState_t encoder_state,
            const nvjpegEncoderParams_t encoder_params,
            const nvjpegImage_t *source,
            nvjpegInputFormat_t input_format,
            int image_width,
            int image_height,
            cudaStream_t stream) nogil
    nvjpegStatus_t nvjpegEncodeRetrieveBitstreamDevice(
            nvjpegHandle_t handle,
            nvjpegEncoderState_t encoder_state,
            unsigned char *data,
            size_t *length,
            cudaStream_t stream) nogil
    nvjpegStatus_t nvjpegEncodeRetrieveBitstream(
            nvjpegHandle_t handle,
            nvjpegEncoderState_t encoder_state,
            unsigned char *data,
            size_t *length,
            cudaStream_t stream) nogil


def get_type() -> str:
    return "nvjpeg"


def get_encodings() -> Sequence[str]:
    return ("jpeg", "jpega")


def get_info() -> Dict[str, Any]:
    return {"version"   : get_version()}


def init_module(options: dict) -> None:
    log("nvjpeg.encoder.init_module(%s) version=%s", options, get_version())
    from xpra.codecs.nvidia.util import has_nvidia_hardware
    if has_nvidia_hardware() is False:
        raise ImportError("no nvidia GPU device found")


def cleanup_module() -> None:
    log("nvjpeg.encoder.cleanup_module()")


NVJPEG_INPUT_FORMATS: Dict[str, Sequence[str]] = {
    "jpeg"  : ("BGRX", "RGBX", ),
    "jpega"  : ("BGRA", "RGBA", ),
}


def get_specs() -> Sequence[VideoSpec]:
    specs: Sequence[VideoSpec] = []
    for encoding, colorspace in NVJPEG_INPUT_FORMATS.items():
        specs.append(VideoSpec(
                encoding="jpeg", input_colorspace=colorspace, output_colorspaces=(colorspace, ),
                has_lossless_mode=False,
                codec_class=Encoder, codec_type="nvjpeg",
                setup_cost=20, cpu_cost=0, gpu_cost=100,
                min_w=16, min_h=16, max_w=16*1024, max_h=16*1024,
                can_scale=True,
                score_boost=-50,
            ),
        )
    return specs


cdef class Encoder:
    cdef unsigned int width
    cdef unsigned int height
    cdef unsigned int encoder_width
    cdef unsigned int encoder_height
    cdef object encoding
    cdef object src_format
    cdef int quality
    cdef int speed
    cdef int grayscale
    cdef long frames
    cdef nvjpegHandle_t nv_handle
    cdef nvjpegEncoderState_t nv_enc_state
    cdef nvjpegEncoderParams_t nv_enc_params
    cdef nvjpegImage_t nv_image
    cdef cudaStream_t stream
    cdef cuda_kernel
    cdef object __weakref__

    def __init__(self):
        self.width = self.height = self.quality = self.speed = self.frames = 0

    def init_context(self, encoding, width : int, height : int, src_format, options: typedict) -> None:
        assert encoding in ("jpeg", "jpega")
        assert src_format in NVJPEG_INPUT_FORMATS[encoding]
        options = options or typedict()
        self.encoding = encoding
        self.width = width
        self.height = height
        self.encoder_width = options.intget("scaled-width", width)
        self.encoder_height = options.intget("scaled-height", height)
        self.src_format = src_format
        self.quality = options.intget("quality", 50)
        self.speed = options.intget("speed", 50)
        self.grayscale = options.boolget("grayscale", False)
        cuda_device_context = options.get("cuda-device-context")
        assert cuda_device_context, "no cuda device context"
        if encoding=="jpeg":
            kernel_name = "%s_to_RGB" % src_format
        else:
            kernel_name = "%s_to_RGBAP" % src_format
        self.stream = NULL
        with cuda_device_context:
            self.cuda_kernel = get_CUDA_function(kernel_name)
        if not self.cuda_kernel:
            raise RuntimeError(f"missing {kernel_name!r} kernel")
        self.init_nvjpeg()

    def init_nvjpeg(self) -> None:
        # initialize nvjpeg structures
        errcheck(nvjpegCreateSimple(&self.nv_handle), "nvjpegCreateSimple")
        errcheck(nvjpegEncoderStateCreate(self.nv_handle, &self.nv_enc_state, self.stream), "nvjpegEncoderStateCreate")
        errcheck(nvjpegEncoderParamsCreate(self.nv_handle, &self.nv_enc_params, self.stream), "nvjpegEncoderParamsCreate")
        self.configure_nvjpeg()

    def configure_nvjpeg(self) -> None:
        self.configure_subsampling(self.grayscale)
        self.configure_quality(self.quality)
        cdef int huffman = int(self.speed<80)
        r = nvjpegEncoderParamsSetOptimizedHuffman(self.nv_enc_params, huffman, self.stream)
        errcheck(r, "nvjpegEncoderParamsSetOptimizedHuffman %i", huffman)
        log("configure_nvjpeg() nv_handle=%#x, nv_enc_state=%#x, nv_enc_params=%#x",
            <uintptr_t> self.nv_handle, <uintptr_t> self.nv_enc_state, <uintptr_t> self.nv_enc_params)
        cdef nvjpegJpegEncoding_t encoding_type = NVJPEG_ENCODING_BASELINE_DCT
        #NVJPEG_ENCODING_EXTENDED_SEQUENTIAL_DCT_HUFFMAN
        #NVJPEG_ENCODING_PROGRESSIVE_DCT_HUFFMAN
        r = nvjpegEncoderParamsSetEncoding(self.nv_enc_params, encoding_type, self.stream)
        errcheck(r, "nvjpegEncoderParamsSetEncoding %i (%s)", encoding_type, ENCODING_STR.get(encoding_type, "invalid"))
        log("configure_nvjpeg() quality=%s, huffman=%s, encoding type=%s",
            self.quality, huffman, ENCODING_STR.get(encoding_type, "invalid"))

    def configure_subsampling(self, grayscale=False) -> None:
        cdef nvjpegChromaSubsampling_t subsampling
        if grayscale:
            subsampling = NVJPEG_CSS_GRAY
        else:
            subsampling = get_subsampling(self.quality)
        cdef int r
        r = nvjpegEncoderParamsSetSamplingFactors(self.nv_enc_params, subsampling, self.stream)
        errcheck(r, "nvjpegEncoderParamsSetSamplingFactors %i (%s)",
                 <const nvjpegChromaSubsampling_t> subsampling, CSS_STR.get(subsampling, "invalid"))
        log("configure_subsampling(%s) using %s", grayscale, CSS_STR.get(subsampling, "invalid"))

    def configure_quality(self, int quality) -> None:
        cdef int r
        r = nvjpegEncoderParamsSetQuality(self.nv_enc_params, self.quality, self.stream)
        errcheck(r, "nvjpegEncoderParamsSetQuality %i", self.quality)

    def is_ready(self) -> bool:
        return self.nv_handle!=NULL

    def is_closed(self) -> bool:
        return self.nv_handle==NULL

    def clean(self) -> None:
        self.clean_cuda()
        self.clean_nvjpeg()

    def clean_cuda(self) -> None:
        self.cuda_kernel = None

    def clean_nvjpeg(self) -> None:
        log("nvjpeg.clean() nv_handle=%#x", <uintptr_t> self.nv_handle)
        if self.nv_handle==NULL:
            return
        self.width = self.height = self.encoder_width = self.encoder_height = self.quality = self.speed = 0
        cdef int r
        r = nvjpegEncoderParamsDestroy(self.nv_enc_params)
        errcheck(r, "nvjpegEncoderParamsDestroy %#x", <uintptr_t> self.nv_enc_params)
        r = nvjpegEncoderStateDestroy(self.nv_enc_state)
        errcheck(r, "nvjpegEncoderStateDestroy")
        r = nvjpegDestroy(self.nv_handle)
        errcheck(r, "nvjpegDestroy")
        self.nv_handle = NULL

    def get_encoding(self) -> str:
        return "jpeg"

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def get_type(self) -> str:
        return "nvjpeg"

    def get_src_format(self) -> str:
        return self.src_format

    def get_info(self) -> Dict[str,Any]:
        info = get_info()
        info |= {
            "frames"        : int(self.frames),
            "width"         : self.width,
            "height"        : self.height,
            "speed"         : self.speed,
            "quality"       : self.quality,
        }
        return info

    def compress_image(self, image, options=None) -> Tuple[bytes, Dict[str, Any]]:
        options = options or {}
        cuda_device_context = options.get("cuda-device-context")
        assert cuda_device_context, "no cuda device context"
        pfstr = image.get_pixel_format().replace("A", "X")
        sfmt = self.src_format.replace("A", "X")
        if sfmt != pfstr:
            raise ValueError("invalid pixel format %s, expected %s" % (image.get_pixel_format(), self.src_format))
        cdef nvjpegInputFormat_t input_format
        quality = options.get("quality", -1)
        if quality>=0 and abs(self.quality-quality)>10:
            self.quality = quality
            self.configure_nvjpeg()
        cdef int width = image.get_width()
        cdef int height = image.get_height()
        cdef int src_stride = image.get_rowstride()
        cdef int dst_stride
        pixels = image.get_pixels()
        cdef Py_ssize_t buf_len = len(pixels)
        cdef double start, end
        cdef size_t length
        cdef MemBuf output_buf
        cdef uintptr_t channel_ptr
        cdef unsigned char* buf_ptr
        for i in range(NVJPEG_MAX_COMPONENT):
            self.nv_image.channel[i] = NULL
            self.nv_image.pitch[i] = 0
        with cuda_device_context as cuda_context:
            start = monotonic()
            #upload raw BGRX / BGRA (or RGBX / RGBA):
            upload_buffer = driver.mem_alloc(buf_len)
            driver.memcpy_htod(upload_buffer, pixels)
            end = monotonic()
            log("nvjpeg: uploaded %i bytes of %s to CUDA buffer %#x in %.1fms",
                buf_len, self.src_format, int(upload_buffer), 1000*(end-start))
            #convert to RGB(A) + scale:
            start = monotonic()
            d = cuda_device_context.device
            da = driver.device_attribute
            blockw = min(32, d.get_attribute(da.MAX_BLOCK_DIM_X))
            blockh = min(32, d.get_attribute(da.MAX_BLOCK_DIM_Y))
            gridw = max(1, ceil(width/blockw))
            gridh = max(1, ceil(height/blockh))
            buffers = []
            client_options = {}
            if self.encoding=="jpeg":
                #use a single RGB buffer as input to the encoder:
                nchannels = 1
                input_format = NVJPEG_INPUT_RGBI
                rgb_buffer, dst_stride = driver.mem_alloc_pitch(self.encoder_width*3, self.encoder_height, 16)
                buffers.append(rgb_buffer)
            else:
                #use planar RGBA:
                nchannels = 4
                input_format = NVJPEG_INPUT_RGB
                dst_stride = 0
                for i in range(nchannels):
                    planar_buffer, planar_stride = driver.mem_alloc_pitch(self.encoder_width, self.encoder_height, 16)
                    buffers.append(planar_buffer)
                    if dst_stride==0:
                        dst_stride = planar_stride
                    else:
                        #all planes are the same size, should get the same stride:
                        assert dst_stride==planar_stride
            def free_buffers():
                for buf in buffers:
                    buf.free()
            args = [
                int32(width), int32(height),
                int32(src_stride), upload_buffer,
                int32(self.encoder_width), int32(self.encoder_height),
                int32(dst_stride),
                ]
            for i in range(nchannels):
                args.append(buffers[i])
                channel_ptr = <uintptr_t> int(buffers[i])
                self.nv_image.channel[i] = <unsigned char *> channel_ptr
                self.nv_image.pitch[i] = dst_stride
            log("nvjpeg calling kernel with %s", args)
            self.cuda_kernel(*args, block=(blockw, blockh, 1), grid=(gridw, gridh))
            cuda_context.synchronize()
            upload_buffer.free()
            del upload_buffer
            end = monotonic()
            log("nvjpeg: csc / scaling took %.1fms", 1000*(end-start))
            if abs(width-self.encoder_width)>1 or abs(height-self.encoder_height)>1:
                client_options["scaling-quality"] = "low"   #our dumb scaling kernels produces low quality output
                client_options["scaled_size"] = self.encoder_width, self.encoder_height
            #now we actually compress the rgb buffer:
            start = monotonic()
            with nogil:
                r = nvjpegEncodeImage(self.nv_handle, self.nv_enc_state, self.nv_enc_params,
                                      &self.nv_image, input_format, self.encoder_width, self.encoder_height, self.stream)
            errcheck(r, "nvjpegEncodeImage")
            end = monotonic()
            log("nvjpeg: nvjpegEncodeImage took %.1fms using input format %s",
                1000*(end-start), NVJPEG_INPUT_STR.get(input_format, input_format))
            #r = cudaStreamSynchronize(stream)
            #if not r:
            #    raise RuntimeError("nvjpeg failed to synchronize cuda stream: %i" % r)
            # get compressed stream size
            start = monotonic()
            r = nvjpegEncodeRetrieveBitstream(self.nv_handle, self.nv_enc_state, NULL, &length, self.stream)
            errcheck(r, "nvjpegEncodeRetrieveBitstream")
            output_buf = getbuf(length, 0)
            buf_ptr = <unsigned char*> output_buf.get_mem()
            with nogil:
                r = nvjpegEncodeRetrieveBitstream(self.nv_handle, self.nv_enc_state, buf_ptr, &length, NULL)
            errcheck(r, "nvjpegEncodeRetrieveBitstream")
            end = monotonic()
            client_options["frame"] = self.frames
            self.frames += 1
            log("nvjpeg: downloaded %i jpeg bytes in %.1fms", length, 1000*(end-start))
            if self.encoding=="jpeg":
                free_buffers()
                return memoryview(output_buf), client_options
            #now compress alpha:
            jpeg = memoryview(output_buf).tobytes()
            start = monotonic()
            #set RGB to the alpha channel:
            for i in range(3):
                self.nv_image.channel[i] = self.nv_image.channel[3]
                self.nv_image.pitch[i] = self.nv_image.pitch[3]
            self.nv_image.channel[3] = NULL
            self.nv_image.pitch[3] = 0
            try:
                #tweak settings temporarily:
                if not self.grayscale:
                    self.configure_subsampling(True)
                if self.quality<100:
                    self.configure_quality(100)
                with nogil:
                    r = nvjpegEncodeImage(self.nv_handle, self.nv_enc_state, self.nv_enc_params,
                                          &self.nv_image, input_format, self.encoder_width, self.encoder_height, self.stream)
                errcheck(r, "nvjpegEncodeImage")
                r = nvjpegEncodeRetrieveBitstream(self.nv_handle, self.nv_enc_state, NULL, &length, self.stream)
                errcheck(r, "nvjpegEncodeRetrieveBitstream")
                output_buf = getbuf(length)
                buf_ptr = <unsigned char*> output_buf.get_mem()
                r = nvjpegEncodeRetrieveBitstream(self.nv_handle, self.nv_enc_state, buf_ptr, &length, NULL)
                errcheck(r, "nvjpegEncodeRetrieveBitstream")
                end = monotonic()
                log("nvjpeg: downloaded %i alpha bytes in %.1fms", length, 1000*(end-start))
                jpega = memoryview(output_buf).tobytes()
                client_options["alpha-offset"] = len(jpeg)
                return jpeg+jpega, client_options
            finally:
                free_buffers()
                #restore settings:
                if not self.grayscale:
                    self.configure_subsampling(False)
                if self.quality<100:
                    self.configure_quality(self.quality)


def compress_file(filename: str, save_to="./out.jpeg") -> None:
    from PIL import Image
    img = Image.open(filename)
    rgb_format = "RGB"
    img = img.convert(rgb_format)
    w, h = img.size
    stride = w*len(rgb_format)
    data = img.tobytes("raw", img.mode)
    log("data=%i bytes (%s) for %s", len(data), type(data), img.mode)
    log("w=%i, h=%i, stride=%i, size=%i", w, h, stride, stride*h)
    from xpra.codecs.image import ImageWrapper
    image = ImageWrapper(0, 0, w, h, data, rgb_format,
                       len(rgb_format)*8, stride, len(rgb_format), ImageWrapper.PACKED, True, None)
    jpeg_data = encode("jpeg", image)[0]
    with open(save_to, "wb") as f:
        f.write(jpeg_data)


cdef nvjpegChromaSubsampling_t get_subsampling(int quality):
    if quality>=80:
        return NVJPEG_CSS_444
    if quality>=60:
        return NVJPEG_CSS_422
    return NVJPEG_CSS_420


def get_device_context():
    cdef double start = monotonic()
    cuda_device_id, cuda_device = select_device()
    if cuda_device_id<0 or not cuda_device:
        raise RuntimeError("failed to select a cuda device")
    log("using device %s", cuda_device)
    cuda_context = cuda_device_context(cuda_device_id, cuda_device)
    cdef double end = monotonic()
    log("device init took %.1fms", 1000*(end-start))
    return cuda_context


errors: List[str] = []
def get_errors() -> Sequence[str]:
    global errors
    return errors


def encode(coding: str, image: ImageWrapper, options=None) -> Tuple:
    if coding not in ("jpeg", "jpega"):
        raise ValueError("invalid encoding: %s" % coding)
    global errors
    pfstr = image.get_pixel_format()
    width = image.get_width()
    height = image.get_height()
    cdef double start, end
    input_formats = NVJPEG_INPUT_FORMATS[coding]
    if pfstr not in input_formats:
        from xpra.codecs.argb.argb import argb_swap # @Reimport
        start = monotonic()
        oldpfstr = pfstr
        if not argb_swap(image, input_formats):
            log("nvjpeg: argb_swap failed to convert %s to a suitable format: %s" % (pfstr, input_formats))
            return ()
        pfstr = image.get_pixel_format()
        end = monotonic()
        log("nvjpeg: argb_swap converted %s to %s in %.1fms", oldpfstr, pfstr, 1000*(end-start))

    options = typedict(options or {})
    if "cuda-device-context" not in options:
        options["cuda-device-context"] = get_device_context()
    cdef Encoder encoder
    try:
        encoder = Encoder()
        encoder.init_context(coding, width, height, pfstr, options=options)
        r = encoder.compress_image(image, options)
        if not r:
            return ()
        cdata, options = r
        may_save_image("jpeg", cdata)
        return coding, Compressed(coding, cdata, False), options, width, height, 0, 24
    except NVJPEG_Exception as e:
        errors.append(str(e))
        return ()
    finally:
        encoder.clean()


def selftest(full=False) -> None:
    from xpra.codecs.nvidia.util import has_nvidia_hardware
    if not has_nvidia_hardware():
        raise ImportError("no nvidia GPU device found")
    from xpra.codecs.checks import make_test_image
    options = {
        "cuda-device-context"   : get_device_context(),
        }
    for width, height in ((32, 32), (256, 80), (1920, 1080)):
        for encoding, input_formats in NVJPEG_INPUT_FORMATS.items():
            for fmt in input_formats:
                img = make_test_image(fmt, width, height)
                log("testing with %s", img)
                v = encode(encoding, img, options)
                assert v, "failed to compress test image"
