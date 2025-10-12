# Fluent UI 투어 (FluTour)

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluTour` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 사용자에게 애플리케이션의 특정 기능이나 UI 요소들을 단계별로 안내하는 가이드 투어를 생성하는 데 사용됩니다.

`FluTour`는 화면 전체에 반투명 오버레이를 표시하고, 현재 단계에서 지정된 UI 요소(`target`) 주변만 밝게 강조하여 사용자의 시선을 집중시킵니다. 동시에 해당 요소에 대한 설명이 담긴 패널을 표시하여 이해를 돕습니다.

## 공통 임포트 방법

`FluTour` 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15 // Popup 기반이므로 필요
import FluentUI 1.0
```

---

## FluTour

`FluTour`는 `Popup` 컨트롤을 기반으로 구현된 컴포넌트로, 애플리케이션의 온보딩 프로세스나 새로운 기능 소개 등에 유용하게 사용될 수 있습니다. 사용자는 '다음', '이전' 버튼을 통해 단계별 안내를 따라갈 수 있으며, 마지막 단계에서는 '완료' 버튼을 통해 투어를 종료합니다.

### 기반 클래스

`Popup` (from `QtQuick.Controls`)

`FluTour`는 `Popup`을 상속하므로, `Popup`에서 제공하는 모든 프로퍼티, 메소드, 시그널을 사용할 수 있습니다. 대표적인 예로는 다음과 같습니다:

*   **주요 상속 프로퍼티**: `visible`, `opened`, `closed`, `padding`, `margins`, `background`, `contentItem`, `focus`, `modal`, `dim` 등
*   **주요 상속 메소드**: `open()`, `close()`
*   **주요 상속 시그널**: `opened()`, `closed()`, `visibleChanged()`

### 주요 프로퍼티

| 이름           | 타입        | 기본값             | 설명                                                                                                                                  |
| :------------- | :---------- | :----------------- | :------------------------------------------------------------------------------------------------------------------------------------ |
| `steps`        | `var` (array)| `[]`               | 투어의 각 단계를 정의하는 JavaScript 객체 배열입니다. 각 객체는 `title`, `description`, `target` 필드를 포함해야 합니다. (상세 내용은 아래 "단계 정의" 섹션 참조) |
| `targetMargins`| `int`       | `5`                | 강조되는 `target` 아이템 주변에 적용될 투명 마스크 영역의 여백 (픽셀 단위)입니다.                                                                        |
| `index`        | `int`       | `0`                | 현재 표시 중인 투어 단계의 인덱스(0부터 시작)입니다. 이 값을 변경하여 프로그래밍 방식으로 특정 단계로 이동할 수 있습니다.                                                     |
| `nextText`     | `string`    | `qsTr("Next")`     | '다음' 버튼에 표시될 텍스트입니다.                                                                                                       |
| `previousText` | `string`    | `qsTr("Previous")` | '이전' 버튼에 표시될 텍스트입니다.                                                                                                       |
| `finishText`   | `string`    | `qsTr("Finish")`   | 투어의 마지막 단계에서 '다음' 버튼 대신 표시될 텍스트입니다.                                                                                             |
| `nextButton`   | `Component` | (내부 FluFilledButton) | '다음' 또는 '완료' 기능을 수행하는 버튼을 생성하는 사용자 정의 컴포넌트입니다. 기본적으로 `FluFilledButton` 컴포넌트가 사용됩니다.                                      |
| `prevButton`   | `Component` | (내부 FluButton)     | '이전' 기능을 수행하는 버튼을 생성하는 사용자 정의 컴포넌트입니다. 기본적으로 `FluButton` 컴포넌트가 사용됩니다.                                                |

### 고유 메소드

`FluTour` 컴포넌트 자체에 정의된 고유 메소드는 없습니다. 투어를 시작하고 종료하려면 `Popup`에서 상속받은 `open()`과 `close()` 메소드를 사용합니다.

### 고유 시그널

`FluTour` 컴포넌트 자체에 정의된 고유 시그널은 없습니다. 투어의 열림/닫힘 상태 변화는 `Popup`에서 상속받은 `opened()`, `closed()`, `visibleChanged()` 시그널을 통해 감지할 수 있습니다.

---

## 단계 정의 (`steps` 프로퍼티)

`FluTour`의 핵심은 `steps` 프로퍼티에 정의된 단계 정보입니다. 이 프로퍼티는 JavaScript 배열 형태이며, 배열의 각 요소는 하나의 투어 단계를 나타내는 객체 리터럴입니다.

각 단계 객체는 다음 세 가지 키-값 쌍을 **반드시** 포함해야 합니다:

*   **`title`**: (`string`)
    해당 단계의 제목입니다. 화면에 표시되는 설명 패널의 상단에 굵은 글씨로 나타납니다.
*   **`description`**: (`string`)
    해당 단계에서 사용자에게 전달할 설명 텍스트입니다. 설명 패널의 본문 영역에 표시됩니다. 여러 줄 입력이 가능합니다.
*   **`target`**: (`function`)
    **매우 중요합니다.** 이 키의 값은 반드시 함수여야 하며, 이 함수는 호출되었을 때 **현재 단계에서 강조하고자 하는 QML 아이템 객체를 반환해야 합니다.** 일반적으로 강조할 아이템의 `id`를 클로저(closure)를 통해 접근하여 반환하는 람다 함수(arrow function) 형태를 사용합니다. 예를 들어, `myButton`이라는 `id`를 가진 버튼을 대상으로 하려면 `target: () => myButton`과 같이 작성합니다.
    투어가 해당 단계로 진행될 때 이 `target` 함수가 동적으로 호출되어 현재 강조할 대상을 결정하고, 그 아이템의 위치와 크기를 기준으로 하이라이트 마스크와 설명 패널의 위치를 계산합니다.

**예시:**

```javascript
steps: [
    { 
        title: qsTr("파일 업로드 영역"), 
        description: qsTr("프로젝트 파일을 이곳으로 드래그 앤 드롭하거나 클릭하여 선택하세요."), 
        target: () => uploadAreaId // uploadAreaId는 대상 아이템의 id
    },
    {
        title: qsTr("설정 버튼"),
        description: qsTr("애플리케이션의 다양한 설정을 변경하려면 이 버튼을 클릭하세요."),
        target: () => settingsButtonId // settingsButtonId는 대상 아이템의 id
    },
    // ... 추가 단계 정의 ...
]
```

---

## 예제

다음은 세 개의 버튼(`btn_upload`, `btn_save`, `btn_more`)을 대상으로 하는 간단한 투어를 정의하고, 'Begin Tour' 버튼을 클릭하여 투어를 시작하는 예제입니다 (`T_Tour.qml` 기반).

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import FluentUI 1.0

FluScrollablePage {
    // ... 페이지 설정 ...

    // FluTour 컴포넌트 정의
    FluTour {
        id: tour
        steps: [
            { title: qsTr("Upload File"), description: qsTr("Put your files here."), target: () => btn_upload },
            { title: qsTr("Save"), description: qsTr("Save your changes."), target: () => btn_save },
            { title: qsTr("Other Actions"), description: qsTr("Click to see other actions."), target: () => btn_more }
        ]
    }

    // 투어 대상이 될 UI 요소들
    FluFrame {
        Layout.fillWidth: true
        padding: 10
        height: 150

        // 투어 시작 버튼
        FluFilledButton {
            anchors.top: parent.top
            anchors.left: parent.left
            text: qsTr("Begin Tour")
            onClicked: {
                tour.open() // FluTour의 open() 메소드 호출
            }
        }

        // 투어 대상 버튼들
        RowLayout {
            anchors.centerIn: parent
            spacing: 20
            
            FluButton {
                id: btn_upload // target 함수에서 참조할 id
                text: qsTr("Upload")
            }
            FluFilledButton {
                id: btn_save // target 함수에서 참조할 id
                text: qsTr("Save")
            }
            FluIconButton {
                id: btn_more // target 함수에서 참조할 id
                iconSource: FluentIcons.More
            }
        }
    }
}
```

위 예제에서 'Begin Tour' 버튼을 클릭하면 `tour.open()`이 호출되어 투어가 시작됩니다. 첫 번째 단계에서는 `btn_upload` 버튼이 강조되고 해당 설명이 표시됩니다. 사용자가 'Next' 버튼을 클릭하면 `btn_save`가 강조되는 두 번째 단계로, 다시 'Next'를 클릭하면 `btn_more`가 강조되는 마지막 단계로 진행됩니다. 마지막 단계에서 'Finish' 버튼을 클릭하면 `tour.close()`가 내부적으로 호출되어 투어가 종료됩니다.

---

## 참고 사항

*   **Overlay 사용**: `FluTour`는 기본적으로 `Overlay.overlay`를 부모로 사용하므로, 현재 활성화된 윈도우의 최상단에 그려집니다. 이는 투어가 다른 모든 UI 요소들 위에 표시되도록 보장합니다.
*   **유효한 `target` 함수**: `steps` 배열의 각 단계에 정의된 `target` 함수는 매우 중요합니다. 이 함수는 해당 단계가 활성화될 때 호출되며, 반드시 **현재 화면에 표시되고 있는 유효한 QML 아이템 객체**를 반환해야 합니다. 만약 `target` 함수가 유효하지 않은 아이템(예: `null`, `undefined`, 또는 숨겨진 아이템)을 반환하면, 해당 단계에서 하이라이트 및 설명 패널 위치가 올바르게 계산되지 않아 오류가 발생하거나 투어가 예상대로 동작하지 않을 수 있습니다.
*   **설명 패널 위치**: 설명 패널(`FluFrame`)은 강조되는 `target` 아이템과의 시각적 충돌을 피하기 위해, 화면 공간을 고려하여 자동으로 대상 아이템의 위 또는 아래에 적절한 위치를 찾아 표시됩니다.
*   **마스크 구현**: 화면 전체를 덮는 반투명 마스크와 `target` 주변의 투명 영역은 내부적으로 `Canvas` 아이템을 사용하여 그려집니다. `target` 주변의 투명 영역은 `targetMargins` 프로퍼티 값을 반영한 둥근 사각형 형태로 그려집니다.
*   **버튼 커스터마이징**: `nextButton`과 `prevButton` 프로퍼티에 사용자가 직접 디자인한 커스텀 버튼 컴포넌트를 지정하여 투어의 네비게이션 버튼 모양을 자유롭게 변경할 수 있습니다. 커스텀 컴포넌트는 'Next', 'Previous', 'Finish' 텍스트와 클릭 로직을 내부적으로 처리해야 할 수 있습니다 (기본 버튼 구현 참고). 