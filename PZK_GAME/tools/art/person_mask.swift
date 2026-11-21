// Person cut-out using macOS Vision (no downloads).
// usage: swift person_mask.swift <input.jpg> <out_prefix>
// Writes <out_prefix>_inst<N>.png for every person instance (white = person),
// plus <out_prefix>_all.png (all people, high-quality segmentation).
import Foundation
import Vision
import CoreImage
import AppKit

let args = CommandLine.arguments
guard args.count >= 3 else { print("usage: in out_prefix"); exit(1) }
let url = URL(fileURLWithPath: args[1])
let prefix = args[2]
let ctx = CIContext()

func save(_ buf: CVPixelBuffer, _ path: String, size: CGSize) {
    var img = CIImage(cvPixelBuffer: buf)
    let sx = size.width / img.extent.width, sy = size.height / img.extent.height
    img = img.transformed(by: CGAffineTransform(scaleX: sx, y: sy))
    let cs = CGColorSpaceCreateDeviceGray()
    if let cg = ctx.createCGImage(img, from: CGRect(origin: .zero, size: size), format: .L8, colorSpace: cs) {
        let rep = NSBitmapImageRep(cgImage: cg)
        try? rep.representation(using: .png, properties: [:])?.write(to: URL(fileURLWithPath: path))
    }
}

guard let src = CIImage(contentsOf: url) else { print("cannot read"); exit(1) }
let size = src.extent.size
let handler = VNImageRequestHandler(url: url)

// 1) high-quality whole-person segmentation
let seg = VNGeneratePersonSegmentationRequest()
seg.qualityLevel = .accurate
seg.outputPixelFormat = kCVPixelFormatType_OneComponent8
try? handler.perform([seg])
if let r = seg.results?.first { save(r.pixelBuffer, prefix + "_all.png", size: size) }

// 2) per-instance masks
let inst = VNGeneratePersonInstanceMaskRequest()
do {
    try handler.perform([inst])
    if let obs = inst.results?.first {
        for i in obs.allInstances {
            if let m = try? obs.generateScaledMaskForImage(forInstances: IndexSet(integer: i), from: handler) {
                save(m, prefix + "_inst\(i).png", size: size)
            }
        }
        print("instances:", Array(obs.allInstances))
    }
} catch { print("instance error", error) }
