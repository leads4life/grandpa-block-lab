"""Rebuild kokoro-q8-timed.onnx from the public Kokoro model (only needed if the copy here is ever lost).
Source: model_quantized.onnx from huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX (Apache-2.0),
sha256 fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478.
The patch adds one output, 'duration' (frames per phoneme), which bl_voice uses for lip sync."""
import sys
import onnx
from onnx import helper, TensorProto
src, dst = (sys.argv[1:] + ["kokoro-q8.onnx", "kokoro-q8-timed.onnx"][len(sys.argv) - 1:])[:2]
m = onnx.load(src)
m.graph.node.append(helper.make_node("Identity", ["/encoder/Round_output_0"], ["duration"], name="duration_out"))
m.graph.output.append(helper.make_tensor_value_info("duration", TensorProto.FLOAT, None))
onnx.save(m, dst)
print("saved", dst)
