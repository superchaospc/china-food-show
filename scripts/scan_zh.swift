// Run with Swift on macOS. Outputs one JSON row per sampled frame, boxes in displayed pixels.
import Foundation
import AVFoundation
import Vision
import CoreGraphics

func stop(_ text: String) -> Never {
    FileHandle.standardError.write(Data((text + "\n").utf8))
    exit(1)
}

let args = Array(CommandLine.arguments.dropFirst())
guard (args.count == 5 || args.count == 6),
      let x = Int(args[1]), let y = Int(args[2]), let width = Int(args[3]), let height = Int(args[4]),
      x >= 0, y >= 0, width > 0, height > 0 else {
    stop("Usage: scan_zh VIDEO X Y WIDTH HEIGHT [STEP_SECONDS], displayed frame coordinates from top left")
}
let step = args.count == 6 ? (Double(args[5]) ?? 0) : 0.2
guard step.isFinite && step >= 0.001 else { stop("Invalid sample step") }
let asset = AVURLAsset(url: URL(fileURLWithPath:args[0]))
let seconds = asset.duration.seconds
guard seconds.isFinite && seconds > 0 else { stop("Invalid source duration") }
let generator = AVAssetImageGenerator(asset:asset)
generator.appliesPreferredTrackTransform = true
generator.requestedTimeToleranceAfter = .zero
// A bounded look-back supports times between frames; report the actual sampled timestamp.
generator.requestedTimeToleranceBefore = CMTime(seconds: min(0.04,step/2), preferredTimescale: 60000)
let roi = CGRect(x:x, y:y, width:width, height:height)
var successful = 0
for i in 0..<Int(ceil(seconds / step)) {
    autoreleasepool {
        let wanted = Double(i)*step
        var actual = CMTime.zero
        var row: [String:Any] = ["sample_seconds":wanted]
        do {
            let full = try generator.copyCGImage(at:CMTime(seconds:wanted,preferredTimescale:60000),actualTime:&actual)
            guard CGRect(x:0,y:0,width:full.width,height:full.height).contains(roi),
                  let crop = full.cropping(to:roi) else { stop("OCR box exceeds the displayed frame") }
            let request = VNRecognizeTextRequest()
            request.recognitionLevel = .accurate
            request.recognitionLanguages = ["zh-Hans","en-US"]
            request.usesLanguageCorrection = false
            try VNImageRequestHandler(cgImage:crop).perform([request])
            row["time_seconds"] = actual.seconds
            row["rows"] = (request.results ?? []).compactMap { result -> [String:Any]? in
                guard let candidate = result.topCandidates(1).first else { return nil }
                let box = result.boundingBox
                return ["text":candidate.string,"confidence":candidate.confidence,
                        "box":[Int((roi.minX + roi.width*box.minX).rounded()),Int((roi.minY + roi.height*(1-box.maxY)).rounded()),
                               Int((roi.width*box.width).rounded()),Int((roi.height*box.height).rounded())]]
            }
            successful += 1
        } catch {
            row["error"] = error.localizedDescription
        }
        do {
            let data = try JSONSerialization.data(withJSONObject:row,options:[.sortedKeys])
            FileHandle.standardOutput.write(data + Data([10]))
        } catch { stop("Cannot encode OCR sample") }
    }
}
if successful == 0 { stop("No OCR sample could be decoded") }
