# Fluent UI 텍스트 스타일 (FluTextStyle)

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluTextStyle` 전역 싱글톤 객체에 대해 설명합니다. `FluTextStyle`은 Fluent Design System의 타이포그래피 가이드라인에 따른 표준 텍스트 스타일 세트를 제공하여 애플리케이션 전체에서 일관된 글꼴 스타일(크기, 굵기 등)을 쉽게 적용할 수 있도록 돕습니다.

## `FluTextStyle` 접근 방법

`FluTextStyle`은 QML 환경에 전역 싱글톤으로 등록되어 있으므로, 어떤 QML 파일에서든 별도의 import 없이 `FluTextStyle` 식별자를 사용하여 직접 접근할 수 있습니다.

```qml
import FluentUI 1.0

FluText {
    text: "This is body text."
    font: FluTextStyle.Body // Body 스타일 적용
}

FluText {
    text: "This is a title."
    font: FluTextStyle.Title // Title 스타일 적용
}
```

Python 코드에서는 다음과 같이 임포트하여 사용할 수 있습니다:
```python
from PySide6.QtGui import QFont
from qtui.FluentUI.plugins import FluTextStyle

text_style = FluTextStyle.getInstance()
caption_font = text_style.Caption
# caption_font를 사용하여 위젯 폰트 설정 등
```

---

## FluTextStyle

`FluTextStyle` 객체는 Fluent Design System에서 정의한 다양한 텍스트 역할(예: 본문, 제목, 캡션)에 해당하는 미리 정의된 `QFont` 객체들을 프로퍼티 형태로 제공합니다. 개발자는 이러한 표준 스타일을 사용함으로써 UI 전체에 걸쳐 타이포그래피의 일관성을 유지하고 디자인 시스템을 준수할 수 있습니다. 각 스타일 프로퍼티는 특정 픽셀 크기와 굵기(Weight)를 가진 `QFont` 객체를 반환합니다.

### 기반 클래스

`QObject` (싱글톤)

### 주요 프로퍼티

`FluTextStyle`의 각 프로퍼티는 특정 텍스트 스타일을 나타내는 `QFont` 객체를 반환합니다.

| 이름        | 타입     | 픽셀 크기 | 굵기 (Weight)  | 설명                     |
| :---------- | :------- | :-------- | :------------- | :----------------------- |
| `Caption`   | `QFont`  | 12        | Normal         | 가장 작은 텍스트 스타일.        |
| `Body`      | `QFont`  | 13        | Normal         | 일반 본문 텍스트 스타일.       |
| `BodyStrong`| `QFont`  | 13        | DemiBold       | 강조된 본문 텍스트 스타일.     |
| `Subtitle`  | `QFont`  | 20        | DemiBold       | 부제목 텍스트 스타일.        |
| `Title`     | `QFont`  | 28        | DemiBold       | 제목 텍스트 스타일.          |
| `TitleLarge`| `QFont`  | 40        | DemiBold       | 큰 제목 텍스트 스타일.       |
| `Display`   | `QFont`  | 68        | DemiBold       | 가장 큰 강조 텍스트 스타일. |
| `family`    | `string` | -         | -              | 모든 스타일에 사용될 기본 글꼴 패밀리. (현재 Windows는 "Arial", 외에는 시스템 기본값) | 

### 주요 시그널

각 폰트 프로퍼티(`Caption`, `Body` 등) 및 `family` 프로퍼티는 값이 변경될 때 해당 `Changed` 시그널(예: `CaptionChanged`, `familyChanged`)을 발생시킵니다. 이를 통해 런타임에 글꼴 스타일이나 패밀리가 변경될 경우 UI를 업데이트할 수 있습니다.

### 메소드

`FluTextStyle`에는 사용자가 직접 호출할 공개 메소드가 없습니다.

### 예제

다음은 QML에서 `FluText` 컴포넌트에 `FluTextStyle`의 다양한 스타일을 적용하는 예시입니다 (`T_Typography.qml` 참조).

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    spacing: 5

    FluText {
        text: "Display Text"
        font: FluTextStyle.Display
    }
    FluText {
        text: "Title Large Text"
        font: FluTextStyle.TitleLarge
    }
    FluText {
        text: "Title Text"
        font: FluTextStyle.Title
    }
    FluText {
        text: "Subtitle Text"
        font: FluTextStyle.Subtitle
    }
    FluText {
        text: "Body Strong Text"
        font: FluTextStyle.BodyStrong
    }
    FluText {
        text: "Body Text"
        font: FluTextStyle.Body
    }
    FluText {
        text: "Caption Text"
        font: FluTextStyle.Caption
    }
}
```

### 참고 사항

*   **싱글톤 접근**: `FluTextStyle`은 싱글톤이므로 애플리케이션 전역에서 하나의 인스턴스만 존재하며, QML에서 `FluTextStyle` 이름으로 직접 접근하여 사용합니다.
*   **`QFont` 객체**: 각 스타일 프로퍼티 (`Caption`, `Body` 등)는 `QFont` 객체를 반환합니다. 이 객체를 `FluText`나 표준 `Text` 컴포넌트의 `font` 프로퍼티에 직접 할당하여 해당 스타일을 적용합니다.
*   **글꼴 패밀리**: `family` 프로퍼티를 통해 기본 글꼴 패밀리를 변경할 수 있지만, 현재 구현에서는 초기 설정 로직이 단순합니다. 기본 글꼴 패밀리를 변경하면 모든 스타일(`Caption`부터 `Display`까지)의 글꼴 패밀리가 함께 변경됩니다. 