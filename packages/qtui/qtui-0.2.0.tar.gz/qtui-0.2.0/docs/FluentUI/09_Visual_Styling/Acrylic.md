# Fluent UI 아크릴 효과 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluAcrylic` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 UI 요소 아래의 배경 콘텐츠에 블러, 색상 틴트, 노이즈 효과를 적용하여 Fluent Design System의 아크릴 머티리얼 효과를 시뮬레이션합니다.

## 공통 임포트 방법

Fluent UI 아크릴 효과 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluAcrylic

`FluAcrylic`은 지정된 `target` 아이템의 일부 영역을 시각적으로 캡처하고, 그 위에 블러 효과, 색상 틴트, 밝기 조정, 노이즈 텍스처를 중첩하여 반투명하고 깊이감 있는 아크릴 재질 효과를 만듭니다. 이 효과는 주로 창 배경, 플라이아웃 메뉴, 대화 상자 등에서 사용하여 앱의 시각적 계층 구조를 강조하고 현대적인 느낌을 줍니다.

내부적으로 `ShaderEffectSource`를 사용하여 타겟 아이템의 이미지를 가져오고, `FastBlur` 그래픽 효과를 적용한 후, 여러 `Rectangle`과 `Image`를 통해 색상 틴트, 밝기, 노이즈를 추가합니다.

### 기반 클래스

`Item`

### 고유/특징적 프로퍼티

| 이름          | 타입    | 기본값                                                       | 설명                                                                                             | 
| :------------ | :------ | :----------------------------------------------------------- | :----------------------------------------------------------------------------------------------- |
| `target`      | `var`   | -                                                            | 아크릴 효과의 배경이 될 QML 아이템입니다. 이 아이템의 시각적 내용이 캡처되어 블러 처리됩니다. **필수적으로 지정해야 합니다.** | 
| `tintColor`   | `color` | `Qt.rgba(1, 1, 1, 1)` (흰색)                               | 아크릴 표면에 적용될 틴트(색조) 색상입니다.                                                          | 
| `tintOpacity` | `real`  | `0.65`                                                       | 틴트 색상의 불투명도입니다 (0.0 ~ 1.0 범위).                                                       | 
| `luminosity`  | `real`  | `0.01`                                                       | 아크릴 효과의 전체적인 밝기를 미세하게 조정합니다. 기본값은 약간의 밝기를 더하는 효과를 줍니다.                               | 
| `noiseOpacity`| `real`  | `0.02`                                                       | 아크릴 표면에 적용될 노이즈 텍스처의 불투명도입니다. 미묘한 질감을 추가하여 유리 느낌을 강화합니다.                                | 
| `blurRadius`  | `int`   | `32`                                                         | 배경에 적용될 블러(흐림) 효과의 반경입니다. 값이 클수록 더 강하게 블러 처리됩니다.                                | 
| `targetRect`  | `rect`  | `Qt.rect(control.x, control.y, control.width, control.height)` | `target` 아이템에서 아크릴 효과의 소스로 사용할 영역을 지정합니다. 기본값은 `FluAcrylic` 컴포넌트 자신의 위치와 크기에 해당하는 영역입니다. | 

### 고유 메소드

`FluAcrylic` 자체에 공개적으로 호출하도록 의도된 고유 메소드는 없습니다.

### 고유 시그널

`FluAcrylic` 자체에서 정의된 고유 시그널은 없습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

FluScrollablePage {
    
    Image {
        id: backgroundImage
        source: "qrc:/example/res/image/bg_scenic.jpg" // 배경 이미지
        width: parent.width
        height: 400
        fillMode: Image.PreserveAspectCrop
    }
    
    // 이미지 위에 FluAcrylic 효과 적용
    FluAcrylic {
        id: acrylicEffect
        width: 250
        height: 150
        anchors.centerIn: backgroundImage // 배경 이미지 중앙에 배치
        
        target: backgroundImage // 효과를 적용할 대상 지정
        tintColor: FluTheme.dark ? Qt.rgba(0,0,0,1) : Qt.rgba(1,1,1,1) // 테마에 따라 틴트 색상 변경
        tintOpacity: 0.7
        blurRadius: 40

        // 아크릴 영역 위에 텍스트 표시
        FluText {
            anchors.centerIn: parent
            text: "Acrylic Effect"
            color: FluTheme.dark ? "white" : "black"
            font: FluTextStyle.Subtitle
        }

        // 마우스로 드래그하여 이동 가능하게 설정 (예시)
        MouseArea {
            property point clickPos: Qt.point(0,0)
            anchors.fill: parent
            onPressed: (mouse) => { clickPos = Qt.point(mouse.x, mouse.y) }
            onPositionChanged: (mouse) => {
                var delta = Qt.point(mouse.x - clickPos.x, mouse.y - clickPos.y)
                acrylicEffect.x += delta.x
                acrylicEffect.y += delta.y
            }
        }
    }
    
    // 속성 제어 예시 (T_Acrylic.qml 참조)
    RowLayout {
        Layout.topMargin: 20
        FluText { text: "Blur Radius:" }
        FluSlider {
            value: acrylicEffect.blurRadius
            to: 100
            onValueChanged: acrylicEffect.blurRadius = value
        }
    }
}
```

### 참고 사항

*   **성능**: 블러 효과는 그래픽 리소스를 많이 사용할 수 있습니다. 특히 `blurRadius` 값이 크거나, 아크릴 효과를 적용하는 영역이 넓거나, `target` 아이템이 자주 변경되는 경우 성능에 영향을 줄 수 있습니다. 필요한 경우에만 제한적으로 사용하는 것이 좋습니다.
*   **`target` 지정**: `FluAcrylic`이 올바르게 작동하려면 반드시 `target` 프로퍼티에 효과를 적용할 배경 아이템을 지정해야 합니다.
*   **`targetRect` 활용**: 기본적으로 `FluAcrylic` 자신의 영역에 해당하는 배경 부분을 사용하지만, `targetRect`를 명시적으로 설정하여 `target` 아이템의 특정 다른 영역을 효과의 소스로 사용할 수 있습니다.
*   **노이즈 텍스처**: 노이즈 효과는 `FluentUI` 모듈 내부에 포함된 `qrc:/Image/noise.png` 이미지 파일을 타일링하여 구현됩니다. 