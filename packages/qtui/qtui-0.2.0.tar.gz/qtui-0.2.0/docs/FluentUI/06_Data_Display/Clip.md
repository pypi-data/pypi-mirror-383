# Fluent UI 클리핑 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluClip` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 자식 요소들을 특정 모양으로 잘라내어(클리핑하여) 표시하는 데 사용됩니다.

## 공통 임포트 방법

Fluent UI 클리핑 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluClip

`FluClip`은 자식 아이템들을 자신이 정의한 모양, 특히 `radius` 프로퍼티로 설정된 둥근 사각형 형태로 마스킹하여 보여주는 컨테이너 컴포넌트입니다. 주로 `Image` 요소의 모서리를 둥글게 처리하거나 다른 시각적 요소들을 특정 형태로 잘라내고 싶을 때 유용하게 사용됩니다. `FluRectangle`을 기반으로 하며, 내부적으로 `Qt5Compat.GraphicalEffects`의 `OpacityMask`를 사용합니다.

### 기반 컴포넌트

`FluRectangle` (및 `OpacityMask` 효과 활용)

### 주요 상속/사용 프로퍼티

| 이름     | 타입         | 기본값         | 설명                                                                                                   |
| :------- | :----------- | :------------- | :----------------------------------------------------------------------------------------------------- |
| `radius` | `list[int]`  | `[0, 0, 0, 0]` | 클리핑 영역의 각 모서리 둥글기 반경을 지정하는 정수 리스트. 순서는 **[top-left, top-right, bottom-right, bottom-left]** 입니다. `FluRectangle`의 프로퍼티를 사용합니다. | 

*   `color` 프로퍼티는 내부적으로 투명(`"#00000000"`)으로 설정되어 클리핑 컨테이너 역할만 수행합니다.
*   `layer.enabled`는 하드웨어 렌더링 환경(`!FluTools.isSoftware()`)에서만 활성화되어 `OpacityMask` 효과를 적용합니다.

### 고유 시그널 / 메소드

`FluClip` 자체에 고유한 시그널이나 메소드는 정의되어 있지 않습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

RowLayout {
    spacing: 14

    // 좌상단만 뾰족하게 클리핑
    FluClip {
        width: 50; height: 50
        radius: [0, 25, 25, 25] // top-left 반경만 0
        Image {
            anchors.fill: parent
            source: "qrc:/example/res/svg/avatar_1.svg"
            sourceSize: Qt.size(parent.width, parent.height)
        }
    }

    // 모든 모서리 약간 둥글게 (반경 10)
    FluClip {
        width: 50; height: 50
        radius: [10, 10, 10, 10]
        Image {
            anchors.fill: parent
            source: "qrc:/example/res/svg/avatar_2.svg"
            sourceSize: Qt.size(parent.width, parent.height)
        }
    }

    // 원형 클리핑 (충분히 큰 반경)
    FluClip {
        width: 50; height: 50
        radius: [25, 25, 25, 25] // 너비/높이의 절반 이상이면 원형이 됨
        Image {
            anchors.fill: parent
            source: "qrc:/example/res/svg/avatar_3.svg"
            sourceSize: Qt.size(parent.width, parent.height)
        }
    }
    
    // 큰 이미지 클리핑
    FluClip{
        width: 1920/5
        height: 1200/5
        radius: [8, 8, 8, 8]
        Image {
            source: "qrc:/example/res/image/banner_1.jpg"
            anchors.fill: parent
            fillMode: Image.PreserveAspectCrop // 이미지가 클리핑 영역을 채우도록
        }
    }
}
```

### 참고 사항

*   **하드웨어 렌더링 필요**: `FluClip`은 `OpacityMask` 그래픽 효과를 사용하므로, QML 애플리케이션이 하드웨어 가속 렌더링 모드로 실행될 때 정상적으로 작동합니다. 소프트웨어 렌더링 환경에서는 클리핑 효과가 적용되지 않을 수 있습니다 (`FluTools.isSoftware()` 확인 로직 참고).
*   **주요 용도**: 이미지나 다른 QML 아이템의 모서리를 둥글게 만들거나 특정 모양으로 잘라내는 데 주로 사용됩니다.
*   **`radius` 프로퍼티**: `FluRectangle` 컴포넌트와 동일하게 작동하며, 네 모서리의 둥근 정도를 개별적으로 지정할 수 있습니다. 