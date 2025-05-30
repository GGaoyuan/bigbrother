import Cocoa
import FlutterMacOS
import bitsdojo_window_macos

class MainFlutterWindow: BitsdojoWindow {
    override func bitsdojo_window_configure() -> UInt {
  return BDW_CUSTOM_FRAME | BDW_HIDE_ON_STARTUP
}

  override func awakeFromNib() {
    let flutterViewController = FlutterViewController()
    let windowFrame = self.frame
    self.contentViewController = flutterViewController
    self.setFrame(windowFrame, display: true)

//     self.titleVisibility = .hidden  // 隐藏标题
//     self.titlebarAppearsTransparent = true // 让标题栏透明
//     self.isMovableByWindowBackground = true // 允许通过背景拖动
//     self.styleMask.remove(.titled) // ❗️去除标题栏样式（如需彻底隐藏）
//     self.styleMask.insert(.fullSizeContentView) // 允许内容区占据整个窗口

    RegisterGeneratedPlugins(registry: flutterViewController)

    super.awakeFromNib()
  }
}
