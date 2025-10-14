from automation_toolkit import AutomationToolkit

# from automation_toolkit.core import AutomationToolkit
tool = AutomationToolkit(
    device="R38N100G4EJ",
    img_path="./images",
    debug_img="./debug",
    ocr_model_path=r"C:\Users\A\PycharmProjects\websoket_ui\ch_PP-OCRv4_det_infer.onnx"
)
# print(tool.compare_region_similarity('image.png', (162, 823, 332, 870),debug=True))
# tool.s
# 使用OCR查找文字
result = tool.ocr_find_text(
    target_text="江湖匆匆",
    region=(968, 962, 1327, 1013),  # 在指定区域查找
    # min_confidence=0.6,
    debug=True
)