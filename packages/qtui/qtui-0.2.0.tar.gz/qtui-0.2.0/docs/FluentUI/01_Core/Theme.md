# Fluent UI 테마 관리 (FluTheme)

이 문서에서는 `FluentUI` 모듈의 핵심 부분인 `FluTheme` 전역 싱글톤 객체에 대해 설명합니다. `FluTheme`은 애플리케이션 전체의 시각적 테마와 관련된 모든 설정(색상 팔레트, 다크/라이트 모드, 애니메이션 등)을 중앙에서 관리합니다.

## `FluTheme` 접근 방법

`FluTheme`은 QML 환경에 전역 싱글톤으로 등록되어 있으므로, 어떤 QML 파일에서든 별도의 import 없이 `FluTheme` 식별자를 사용하여 직접 접근할 수 있습니다.

```qml
// 예시: 다크 모드 활성화
FluTheme.darkMode = FluThemeType.Dark 

// 예시: 강조 색상 변경
FluTheme.accentColor = FluColors.Teal

// 예시: 현재 배경색 사용
Rectangle {
    color: FluTheme.backgroundColor
}
```

Python 코드에서는 다음과 같이 임포트하여 사용할 수 있습니다:
```python
from qtui.FluentUI.plugins import FluTheme, FluColors, FluThemeType

theme = FluTheme.getInstance()
theme.darkMode = FluThemeType.DarkMode.Light
theme.accentColor = FluColors.Purple
```

---

## FluTheme

`FluTheme` 객체는 Fluent UI QML 애플리케이션의 시각적 스타일과 동작을 제어하는 중심점입니다. 사용자는 `FluTheme`의 프로퍼티를 변경하여 애플리케이션의 강조 색상, 다크/라이트 모드 전환, 애니메이션 활성화 여부, 네이티브 텍스트 렌더링 사용 여부 등을 실시간으로 변경할 수 있습니다. 이 변경 사항은 `FluTheme`의 프로퍼티에 바인딩된 모든 UI 요소에 자동으로 전파되어 즉시 반영됩니다.

특히 `darkMode` 프로퍼티를 `FluThemeType.System`으로 설정하면, `FluTheme`은 운영체제의 현재 다크 모드 설정을 감지하고 이를 애플리케이션 테마에 자동으로 동기화합니다.

### 기반 클래스

`QObject` (싱글톤)

### 주요 프로퍼티

| 이름                     | 타입                  | 기본값                        | 설명                                                                                                                                                              |
| :----------------------- | :-------------------- | :---------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `accentColor`            | `FluAccentColor`      | `FluColors.Blue`              | 애플리케이션의 주 강조 색상입니다. `FluColors`에 정의된 객체 또는 `FluColors.createAccentColor()`로 생성된 객체를 할당합니다. 파생 색상들이 이 값을 기반으로 업데이트됩니다.                    |
| `darkMode`               | `FluThemeType.DarkMode`| `FluThemeType.Light`         | 테마 모드를 설정합니다 (`Light`=0, `Dark`=1, `System`=2). `System` 선택 시 OS 설정을 따릅니다.                                                                      |
| `dark`                   | `readonly bool`       | (계산됨)                     | 현재 *실제로* 적용된 테마가 다크 모드인지 여부를 나타냅니다 (`true`/`false`). `darkMode`와 시스템 설정을 종합하여 결정됩니다.                                                              |
| `nativeText`             | `bool`                | `false`                       | `FluText` 등에서 플랫폼 네이티브 텍스트 렌더링 엔진을 사용할지 여부를 설정합니다.                                                                                        |
| `animationEnabled`       | `bool`                | `true`                        | Fluent UI 컴포넌트 내의 전환 및 상태 변경 애니메이션을 전역적으로 활성화/비활성화합니다.                                                                                  |
| `blurBehindWindowEnabled`| `bool`                | `false`                       | 창 배경 뒤에 현재 데스크탑 배경화면을 블러 처리하여 표시하는 효과를 활성화합니다. 성능에 영향을 줄 수 있습니다.                                                                     |
| `desktopImagePath`       | `readonly string`     | ""                          | `blurBehindWindowEnabled`가 `true`일 때 자동으로 감지된 현재 데스크탑 배경화면 이미지 파일의 경로입니다.                                                                             |

### 파생 색상 프로퍼티 (Derived Colors)

`FluTheme`은 `accentColor`와 `dark` 상태에 따라 UI 요소들이 사용할 다양한 색상들을 자동으로 계산하여 제공합니다. 모든 파생 색상 프로퍼티는 변경 시 해당 `Changed` 시그널을 발생시킵니다. 주요 파생 색상은 다음과 같습니다:

*   `primaryColor`: `QColor` - 주 강조 색상 (상태에 따라 `accentColor`의 특정 음영 사용)
*   `backgroundColor`: `QColor` - 앱/컴포넌트의 기본 배경색
*   `windowBackgroundColor`: `QColor` - 창 영역의 기본 배경색
*   `windowActiveBackgroundColor`: `QColor` - 활성 창의 배경색
*   `fontPrimaryColor`, `fontSecondaryColor`, `fontTertiaryColor`: `QColor` - 주/보조/3차 텍스트 색상
*   `itemNormalColor`, `itemHoverColor`, `itemPressColor`, `itemCheckColor`: `QColor` - 상호작용 가능한 아이템의 상태(기본, 호버, 누름, 선택됨)에 따른 배경/오버레이 색상
*   `frameColor`, `frameActiveColor`: `QColor` - 창 테두리/프레임 색상 (비활성/활성 상태)
*   `dividerColor`: `QColor` - 구분선의 색상

(전체 목록 및 정확한 색상 계산 로직은 `FluTheme.py` 소스 코드의 `_refreshColors` 메소드를 참조하십시오.)

### 주요 시그널

주요 프로퍼티 값이 변경될 때 해당 시그널이 발생합니다. 모든 프로퍼티는 `[propertyName]Changed` 형태의 시그널을 가집니다.

*   `accentColorChanged()`
*   `darkModeChanged()`
*   `darkChanged()`
*   `nativeTextChanged()`
*   `animationEnabledChanged()`
*   `blurBehindWindowEnabledChanged()`
*   `primaryColorChanged()`, `backgroundColorChanged()`, 등 (모든 파생 색상 포함)

### 메소드

`FluTheme`에는 사용자가 테마 설정을 위해 직접 호출할 공개 메소드가 없습니다. 모든 설정 변경은 프로퍼티 할당을 통해 이루어집니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    spacing: 10

    FluText { text: "테마 설정" }

    RowLayout {
        FluText { text: "강조 색상:" }
        // 미리 정의된 색상 버튼들 (T_Theme.qml 참조)
        Rectangle { 
            width: 30; height: 30; radius: 4; color: FluColors.Orange.normal
            MouseArea { anchors.fill: parent; onClicked: FluTheme.accentColor = FluColors.Orange }
        }
        Rectangle { 
            width: 30; height: 30; radius: 4; color: FluColors.Blue.normal
            MouseArea { anchors.fill: parent; onClicked: FluTheme.accentColor = FluColors.Blue }
        }
        // 사용자 정의 색상 피커 (T_Theme.qml 참조)
        FluColorPicker {
            current: FluTheme.accentColor.normal
            onAccepted: FluTheme.accentColor = FluColors.createAccentColor(current)
        }
    }
    
    RowLayout {
        FluText { text: "다크 모드:" }
        FluComboBox {
            items: ["Light", "Dark", "System"]
            currentIndex: FluTheme.darkMode
            onCurrentIndexChanged: FluTheme.darkMode = currentIndex // 0: Light, 1: Dark, 2: System
        }
        FluText { text: "(현재 상태: " + (FluTheme.dark ? "Dark" : "Light") + ")" }
    }
    
    FluToggleSwitch {
        text: "네이티브 텍스트 렌더링"
        checked: FluTheme.nativeText
        onClicked: FluTheme.nativeText = !FluTheme.nativeText
    }
    
    FluToggleSwitch {
        text: "애니메이션 활성화"
        checked: FluTheme.animationEnabled
        onClicked: FluTheme.animationEnabled = !FluTheme.animationEnabled
    }
    
    FluToggleSwitch {
        text: "창 배경 블러 효과"
        checked: FluTheme.blurBehindWindowEnabled
        onClicked: FluTheme.blurBehindWindowEnabled = !FluTheme.blurBehindWindowEnabled
    }
}
```

### 관련 클래스/객체

*   **`FluColors`**: `Blue`, `Orange`, `Red` 등 미리 정의된 `FluAccentColor` 객체들을 속성으로 제공합니다. 또한, `createAccentColor(color: QColor)` 정적 메소드를 통해 `QColor` 객체로부터 새로운 `FluAccentColor` 객체를 생성할 수 있습니다.
*   **`FluAccentColor`**: 특정 강조 색상의 여러 음영(예: `normal`, `light`, `dark`)을 포함하는 객체입니다. `FluTheme`은 현재 테마 모드(dark/light)에 따라 이 음영들을 사용하여 `primaryColor` 등의 파생 색상을 결정합니다.
*   **`FluThemeType`**: `DarkMode` 열거형(`Enum`)을 포함하며, `Light` (0), `Dark` (1), `System` (2) 세 가지 값을 가집니다.

### 참고 사항

*   `FluTheme`은 싱글톤 패턴으로 구현되어 애플리케이션 전역에서 단 하나의 인스턴스만 존재하며, QML 컨텍스트에 자동으로 등록됩니다.
*   `FluTheme`의 프로퍼티를 변경하면, 해당 프로퍼티에 바인딩된 모든 UI 요소의 모습이 실시간으로 업데이트됩니다.
*   `blurBehindWindowEnabled` 옵션은 시스템의 데스크탑 배경화면 이미지를 읽고 실시간 블러 효과를 적용해야 하므로, 다른 옵션에 비해 상대적으로 높은 시스템 리소스를 요구할 수 있습니다.
*   `darkMode` 프로퍼티는 사용자의 테마 *설정* (Light, Dark, System 모드 중 선택)을 나타내는 반면, `dark` 프로퍼티는 시스템 설정을 포함하여 *현재 실제로 적용된* 다크 모드 상태 (`true` 또는 `false`)를 나타내는 읽기 전용 값입니다. 