import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


class FontManager:
    """
    Mac 환경에서 Matplotlib 한글 폰트를 자동 설정하거나 순환 변경할 수 있는 간단한 유틸리티
    """

    def __init__(self, fonts_dir="/Library/Fonts"):
        self.fonts_dir = fonts_dir
        self.ttf_paths = [
            os.path.join(fonts_dir, f)
            for f in os.listdir(fonts_dir)
            if f.lower().endswith(".ttf")
        ]

        if not self.ttf_paths:
            raise FileNotFoundError(f"No .ttf fonts found in {fonts_dir}")

        self.n = 0
        self.ttf_path = self.ttf_paths[self.n]
        self._apply_font()

    def _apply_font(self):
        """현재 선택된 폰트를 matplotlib에 적용"""
        font_name = fm.FontProperties(fname=self.ttf_path).get_name()
        plt.rc("font", family=font_name)
        plt.rcParams["axes.unicode_minus"] = False  # 한글 깨짐 방지
        print(f"✅ 현재 폰트 적용됨: {font_name}")

    def next(self):
        """다음 폰트로 순환"""
        self.n = (self.n + 1) % len(self.ttf_paths)
        self.ttf_path = self.ttf_paths[self.n]
        self._apply_font()

    def set(self, font_name: str):
        """특정 폰트 이름으로 설정"""
        matched = [
            path
            for path in self.ttf_paths
            if fm.FontProperties(fname=path).get_name() == font_name
        ]
        if not matched:
            print(f"❌ '{font_name}' 폰트를 찾을 수 없습니다.")
            return
        self.ttf_path = matched[0]
        self._apply_font()

    def list_fonts(self):
        """사용 가능한 폰트 목록 출력"""
        fonts = [fm.FontProperties(fname=p).get_name() for p in self.ttf_paths]
        for i, f in enumerate(fonts, 1):
            print(f"{i}. {f}")
        return fonts


# --- 간단한 전역 인터페이스 제공 ---
_manager = None


def auto(fonts_dir="/Library/Fonts"):
    """자동으로 한글 폰트 설정"""
    global _manager
    _manager = FontManager(fonts_dir)
    return _manager


def next_font():
    """다음 폰트로 순환"""
    if _manager:
        _manager.next()
    else:
        print("⚠️ 먼저 pltfont.auto()를 실행하세요.")


def list_fonts():
    """폰트 목록 확인"""
    if _manager:
        return _manager.list_fonts()
    else:
        print("⚠️ 먼저 pltfont.auto()를 실행하세요.")


def set(font_name: str):
    """특정 폰트로 설정"""
    if _manager:
        _manager.set(font_name)
    else:
        print("⚠️ 먼저 pltfont.auto()를 실행하세요.")
