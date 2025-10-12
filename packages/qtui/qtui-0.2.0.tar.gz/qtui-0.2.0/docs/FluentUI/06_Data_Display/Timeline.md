# Fluent UI 타임라인 (FluTimeline)

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluTimeline` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 시간 순서에 따라 발생하는 이벤트, 단계, 로그 등 일련의 데이터를 수직적인 타임라인 형태로 시각화하는 데 사용됩니다.

## 공통 임포트 방법

`FluTimeline` 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluTimeline

`FluTimeline`은 제공된 데이터 모델(`model` 프로퍼티)을 기반으로 각 항목을 시간 순서대로 표시하는 시각적 컴포넌트입니다. 내부적으로 `Repeater`를 사용하여 모델의 각 요소에 대해 타임라인 선 위의 점(dot) 노드와 해당 내용을 렌더링합니다. `mode` 프로퍼티를 통해 항목들이 타임라인 선을 기준으로 정렬되는 방식을 제어할 수 있습니다.

### 기반 클래스

`Item` (from `QtQuick`)

### 주요 프로퍼티

| 이름        | 타입                  | 기본값          | 설명                                                                                                                               |
| :---------- | :-------------------- | :-------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| `model`     | `var` (alias)         | `undefined`     | 타임라인에 표시할 데이터 모델입니다. `ListModel`, `ObjectModel` 등 `Repeater`에서 사용할 수 있는 모든 모델 타입을 지원합니다. (내부 `Repeater.model` 별칭)         |
| `mode`      | `int` (`FluTimelineType`) | `FluTimelineType.Left` | 타임라인 항목의 레이아웃 모드를 지정합니다. (`Left`, `Right`, `Alternate` 중 하나, 상세 내용은 아래 "레이아웃 모드" 섹션 참조)                               |
| `lineColor` | `color`               | (테마 의존적)    | 타임라인의 중심 수직선의 색상입니다. 기본값은 현재 테마(`FluTheme`)에 따라 결정됩니다 (Dark: `#505050`, Light: `#D2D2D2`).                                    |

### 고유 메소드

`FluTimeline` 컴포넌트에는 QML에서 직접 호출할 수 있는 고유 메소드가 없습니다.

### 고유 시그널

`FluTimeline` 컴포넌트에는 QML에서 직접 연결하여 사용할 수 있는 고유 시그널이 없습니다.

---

## 모델 데이터 정의 (`model` 프로퍼티)

`FluTimeline`은 `model` 프로퍼티에 할당된 데이터 모델을 기반으로 내용을 표시합니다. 일반적으로 `ListModel`을 사용하며, 각 `ListElement`는 타임라인의 한 단계를 나타냅니다. 각 `ListElement`는 다음과 같은 역할(role) 또는 프로퍼티를 가질 수 있습니다.

*   **`text`**: (`string`, **필수**)
    해당 타임라인 항목의 주요 내용이나 설명을 담는 텍스트입니다. 이 텍스트는 리치 텍스트 형식을 지원하므로, `Qt`의 지원 범위 내에서 HTML 태그를 사용하여 텍스트 서식, 이미지(`<img>`), 하이퍼링크(`<a>`) 등을 포함할 수 있습니다.

*   **`lable`**: (`string`, 선택 사항)
    타임라인 항목에 대한 추가적인 레이블 또는 타임스탬프를 표시하는 텍스트입니다. 주로 날짜, 시간, 단계 제목 등을 나타내는 데 사용됩니다. 표시되는 위치는 `mode` 설정에 따라 달라집니다.

*   **`dot`**: (`Component`, 선택 사항)
    타임라인 선 위에 각 항목을 표시하는 기본 원형 점(dot) 대신 사용할 사용자 정의 컴포넌트를 지정합니다. 이 프로퍼티의 값은 **컴포넌트를 반환하는 함수**여야 합니다 (예: `dot: () => myCustomDotComponentId`). 이를 통해 각 항목의 마커 모양을 개별적으로 또는 전체적으로 변경할 수 있습니다.

*   **`lableDelegate`**: (`Component`, 선택 사항)
    `lable` 텍스트를 렌더링하는 데 사용될 사용자 정의 컴포넌트를 지정합니다. 이 프로퍼티의 값은 **컴포넌트를 반환하는 함수**여야 합니다 (예: `lableDelegate: () => myCustomLabelComponentId`). 기본적으로 `FluText`가 사용되지만, 이 델리게이트를 사용하여 레이블에 특정 스타일을 적용하거나 클릭과 같은 상호작용을 추가할 수 있습니다. 델리게이트 내부에서는 `modelData` 프로퍼티를 통해 해당 모델 요소 데이터에 접근할 수 있습니다.

*   **`textDelegate`**: (`Component`, 선택 사항)
    `text` 내용을 렌더링하는 데 사용될 사용자 정의 컴포넌트를 지정합니다. 이 프로퍼티의 값은 **컴포넌트를 반환하는 함수**여야 합니다 (예: `textDelegate: () => myCustomTextComponentId`). 기본적으로 리치 텍스트를 지원하는 `FluText`가 사용되지만, 이 델리게이트를 사용하여 내용 표시에 대한 완전한 제어를 얻거나, 특히 리치 텍스트 내 링크의 활성화(`onLinkActivated`) 및 호버(`onLinkHovered`) 이벤트를 처리하는 등의 고급 기능을 구현할 수 있습니다. 델리게이트 내부에서는 `modelData` 프로퍼티를 통해 해당 모델 요소 데이터에 접근할 수 있습니다.

**ListModel 예시:**

```qml
ListModel {
    ListElement {
        lable: "2023-01-15"
        text: "프로젝트 시작. <b>요구사항 분석</b> 완료."
    }
    ListElement {
        lable: "2023-03-01"
        text: "디자인 프로토타입 공개. <a href='http://example.com'>피드백 요청</a>"
        dot: () => customMilestoneDot // 사용자 정의 마커 사용
        textDelegate: () => richTextDelegate // 링크 처리 등을 위한 커스텀 텍스트 델리게이트
    }
    // ... more elements
}
```

---

## 레이아웃 모드 (`mode`)

`mode` 프로퍼티는 타임라인 항목들이 수직선을 기준으로 어떻게 배치될지를 결정합니다. `FluTimelineType` 열거형에 정의된 다음 값 중 하나를 사용합니다:

*   **`FluTimelineType.Left` (0)**: 타임라인 선이 컴포넌트의 **왼쪽**에 위치합니다. 모든 항목 내용(`text`)과 레이블(`lable`)은 선의 **오른쪽**에 표시됩니다.
*   **`FluTimelineType.Right` (1)**: 타임라인 선이 컴포넌트의 **오른쪽**에 위치합니다. 모든 항목 내용(`text`)과 레이블(`lable`)은 선의 **왼쪽**에 표시됩니다.
*   **`FluTimelineType.Alternate` (2)**: 타임라인 선이 컴포넌트의 **중앙**에 위치합니다. 항목 내용은 선의 **왼쪽**과 **오른쪽**에 번갈아 가며 표시됩니다 (첫 번째 항목은 왼쪽에 표시됨). `lable`이 있는 경우, 항상 `text` 내용의 **반대편**에 표시되어 균형 잡힌 레이아웃을 이룹니다. 모델 요소에 `lable`이 정의되어 있지 않으면, 해당 영역은 비어 있게 됩니다.

---

## 예제

다음은 `ListModel` 데이터를 사용하여 타임라인을 생성하고, 사용자 정의 델리게이트와 리치 텍스트를 활용하며, `FluDropDownButton`으로 레이아웃 모드를 동적으로 변경하는 예제입니다 (`T_Timeline.qml` 기반).

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import FluentUI 1.0

FluScrollablePage {

    // --- 사용자 정의 델리게이트 정의 ---
    Component {
        id: com_dot_custom
        Rectangle {
            width: 16; height: 16; radius: 8
            border.width: 4
            border.color: FluTheme.dark ? FluColors.Teal.lighter : FluColors.Teal.dark
            color: FluTheme.dark ? "#333" : "#EEE"
        }
    }

    Component {
        id: com_lable_interactive
        FluText {
            wrapMode: Text.WrapAnywhere
            font.bold: true
            horizontalAlignment: isRight ? Qt.AlignRight : Qt.AlignLeft // 델리게이트 내부에서 isRight 사용 가능
            text: modelData.lable // modelData 통해 모델 데이터 접근
            color: FluTheme.dark ? FluColors.Teal.lighter : FluColors.Teal.dark
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    console.log("Label clicked:", modelData.lable)
                    // 추가적인 클릭 이벤트 처리
                }
            }
        }
    }

    Component {
        id: com_text_richtext
        FluText {
            wrapMode: Text.WrapAnywhere
            horizontalAlignment: isRight ? Qt.AlignRight : Qt.AlignLeft
            text: modelData.text
            textFormat: Text.RichText // 리치 텍스트 활성화
            linkColor: FluTheme.dark ? FluColors.Teal.lighter : FluColors.Teal.dark
            // 링크 활성화 및 호버 처리
            onLinkActivated: (link) => { Qt.openUrlExternally(link) }
            onLinkHovered: (link) => { FluTools.setOverrideCursor(link ? Qt.PointingHandCursor : Qt.ArrowCursor) }
        }
    }

    // --- 데이터 모델 정의 ---
    ListModel {
        id: timelineModel
        ListElement { lable:"2023-01-01"; text:"<b>새해 시작!</b><br/>새로운 목표 설정" }
        ListElement { lable:"2023-05-15"; text:"중간 점검 및 <a href='https://fluentui.com'>Fluent UI</a> 학습 시작"; dot: () => com_dot_custom; lableDelegate: () => com_lable_interactive }
        ListElement { lable:"2023-09-30"; text:"프로젝트 마일스톤 달성<br/><img src='qrc:/example/res/image/avatar.png' width='60'> 포함" ; textDelegate: () => com_text_richtext }
        ListElement { lable:"2023-12-31"; text:"연말 회고 및 내년 계획" }
    }

    // --- UI 구성 ---
    ColumnLayout {
        anchors.fill: parent
        padding: 10
        spacing: 15

        RowLayout { // 모드 변경 컨트롤
            FluText { text: "Mode:" }
            FluDropDownButton {
                id: modeButton
                text: "Alternate"
                FluMenuItem { text: "Left"; onClicked: { modeButton.text = text; timeline.mode = FluTimelineType.Left } }
                FluMenuItem { text: "Right"; onClicked: { modeButton.text = text; timeline.mode = FluTimelineType.Right } }
                FluMenuItem { text: "Alternate"; onClicked: { modeButton.text = text; timeline.mode = FluTimelineType.Alternate } }
            }
        }

        FluTimeline {
            id: timeline
            Layout.fillWidth: true
            Layout.topMargin: 20
            model: timelineModel
            mode: FluTimelineType.Alternate // 초기 모드 설정
        }
    }
}
```

---

## 참고 사항

*   **높이 자동 조절**: `FluTimeline`의 전체 높이는 내부 `Repeater`에 의해 생성된 컨텐츠의 총 높이에 따라 동적으로 결정됩니다. 스크롤 가능한 영역 내에 배치하는 것이 일반적입니다.
*   **리치 텍스트 활용**: `text` 역할에 HTML과 유사한 태그를 사용하여 텍스트 서식, 이미지 삽입, 하이퍼링크 등을 구현할 수 있습니다. 이를 제대로 표시하려면 기본 또는 사용자 정의 `textDelegate`에서 `textFormat: Text.RichText`를 설정해야 합니다.
*   **델리게이트 커스터마이징**: `dot`, `lableDelegate`, `textDelegate` 프로퍼티를 사용하면 각 타임라인 항목의 시각적 표현과 상호작용을 매우 유연하게 제어할 수 있습니다. 각 델리게이트 컴포넌트 내에서는 `modelData`라는 이름으로 해당 모델 요소의 데이터에 접근할 수 있으며, `isRight`라는 boolean 프로퍼티를 통해 현재 항목이 타임라인 선의 오른쪽에 배치되는지 여부를 알 수 있습니다(주로 `Alternate` 모드에서 유용).
*   **성능**: 매우 많은 수의 항목(수백 개 이상)을 타임라인에 표시해야 하는 경우, `Repeater`의 특성상 초기 로딩 및 스크롤 성능에 영향을 줄 수 있습니다. 필요하다면 모델 데이터 페이징이나 지연 로딩 같은 기법을 고려해야 할 수 있습니다. 