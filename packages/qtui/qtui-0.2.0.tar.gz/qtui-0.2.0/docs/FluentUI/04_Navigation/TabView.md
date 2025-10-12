# Fluent UI 탭 뷰 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluTabView` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 사용자가 여러 문서나 페이지를 탭 형태로 관리하고 쉽게 전환할 수 있는 인터페이스를 제공합니다.

## 공통 임포트 방법

Fluent UI 탭 뷰 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
// 필요에 따라 Layouts, Controls 등 추가
import QtQuick.Layouts 1.15 
import QtQuick.Controls 2.15
```

---

## FluTabView

`FluTabView`는 웹 브라우저의 탭과 유사한 사용자 인터페이스를 제공합니다. 상단에는 각 탭을 나타내는 헤더 영역이 있고, 그 아래에는 현재 선택된 탭에 해당하는 콘텐츠가 표시됩니다. 사용자는 탭을 클릭하여 전환하고, 탭의 닫기 버튼으로 탭을 제거하며, '새 탭' 버튼으로 새 탭을 추가하고, 드래그 앤 드롭으로 탭 순서를 변경할 수 있습니다.

### 기반 클래스

`Item`

### `FluTabViewType` 열거형

`FluTabView`의 일부 프로퍼티는 다음 `FluTabViewType` 열거형 값을 사용합니다:

*   탭 너비 동작 (`tabWidthBehavior`):
    *   `FluTabViewType.Equal`: 모든 탭이 동일한 너비를 가지도록 공간을 균등하게 분할합니다 (최대 너비 제한 있음).
    *   `FluTabViewType.SizeToContent`: 모든 탭이 `itemWidth` 프로퍼티에 지정된 너비를 가집니다.
    *   `FluTabViewType.Compact`: 탭이 활성화되거나 마우스 호버 시에만 `itemWidth` 너비를 가지며, 그 외에는 아이콘과 닫기 버튼만 표시될 정도의 최소 너비를 가집니다.
*   닫기 버튼 표시 (`closeButtonVisibility`):
    *   `FluTabViewType.Always`: 닫기 버튼을 항상 표시합니다.
    *   `FluTabViewType.OnHover`: 마우스 커서가 탭 위에 있을 때만 닫기 버튼을 표시합니다.
    *   `FluTabViewType.Never`: 닫기 버튼을 표시하지 않습니다.

### 고유/특징적 프로퍼티

| 이름                   | 타입 | 기본값                   | 설명                                                                                                                                         |
| :--------------------- | :--- | :----------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| `tabWidthBehavior`     | `int`| `FluTabViewType.Equal`   | 탭 헤더의 너비 계산 방식을 지정합니다. `FluTabViewType` 열거형 값(`Equal`, `SizeToContent`, `Compact`) 중 하나를 사용합니다.                               |
| `closeButtonVisibility`| `int`| `FluTabViewType.Always`  | 각 탭의 닫기 버튼 표시 정책을 지정합니다. `FluTabViewType` 열거형 값(`Always`, `OnHover`, `Never`) 중 하나를 사용합니다.                                |
| `itemWidth`            | `int`| `146`                    | `tabWidthBehavior`가 `SizeToContent` 또는 `Compact`일 때 사용되는 탭의 고정 너비 또는 확장 시 너비입니다.                                                       |
| `addButtonVisibility`  | `bool`| `true`                   | 탭 목록 오른쪽에 '새 탭 추가'(+) 버튼을 표시할지 여부를 결정합니다.                                                                                |

*   내부적으로 탭 모델(`tab_model`: `ListModel`), 탭 네비게이션(`tab_nav`: `ListView`), 콘텐츠 컨테이너(`container`: `Item`) 등을 사용합니다.

### 고유 시그널

| 이름         | 파라미터 | 반환타입 | 설명                                            |
| :----------- | :------- | :------- | :---------------------------------------------- |
| `newPressed` | 없음     | -        | '새 탭 추가'(+) 버튼이 클릭되었을 때 발생하는 시그널입니다. | 

### 고유 메소드

| 이름         | 파라미터                                           | 반환타입 | 설명                                                                                                                               |
| :----------- | :------------------------------------------------- | :------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| `createTab`  | `string`: `icon`, `string`: `text`, `Component`: `page`, `var`: `argument` (기본값 `{}`) | `object` | 주어진 정보로 탭 데이터를 나타내는 JavaScript 객체(`{icon, text, page, argument}`)를 생성하여 반환합니다.                                                 |
| `appendTab`  | `string`: `icon`, `string`: `text`, `Component`: `page`, `var`: `argument`           | `void`   | `createTab` 메소드를 사용하여 새 탭 데이터를 만들고, 이를 내부 모델(`tab_model`)의 끝에 추가합니다. 이 메소드를 호출하면 새 탭이 인터페이스에 나타납니다.                     |
| `setTabList` | `list<object>`: `list`                           | `void`   | 현재 탭 모델의 모든 항목을 제거하고, 제공된 `list` (탭 데이터 객체의 배열)로 모델을 새로 설정합니다.                                                                 |
| `count`      | 없음                                               | `int`    | 현재 `FluTabView`에 열려 있는 탭의 총 개수를 반환합니다.                                                                                  |

### 탭 데이터 구조

`appendTab` 또는 `setTabList` 메소드에 사용되는 탭 데이터 객체는 다음과 같은 프로퍼티를 가집니다:

*   `icon`: `string` - 탭 헤더에 표시될 아이콘의 경로 (예: `"qrc:/images/my_icon.png"`).
*   `text`: `string` - 탭 헤더에 표시될 텍스트 제목.
*   `page`: `Component` - 해당 탭이 선택되었을 때 콘텐츠 영역에 표시될 QML 컴포넌트. 반드시 `Component { ... }` 형태로 지정해야 합니다.
*   `argument`: `var` (선택 사항) - `page` 컴포넌트가 로드될 때 전달할 추가적인 데이터입니다. 로드된 컴포넌트 내에서는 `argument`라는 이름의 프로퍼티로 이 데이터에 접근할 수 있습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

FluWindow {
    width: 800
    height: 600
    visible: true

    property int tabCounter: 1

    // 탭 콘텐츠로 사용될 간단한 컴포넌트 정의
    Component {
        id: pageComponent
        Rectangle {
            color: argument.bgColor // argument로 전달된 색상 사용
            FluText {
                text: "탭 " + argument.tabNum + " 콘텐츠"
                anchors.centerIn: parent
                font.pointSize: 16
            }
        }
    }

    // 새 탭 추가 함수
    function addNewTab() {
        var newTitle = "문서 " + tabCounter
        var newArgument = { bgColor: FluColors.getRandomColor(), tabNum: tabCounter }
        tabView.appendTab("qrc:/path/to/your/icon.png", newTitle, pageComponent, newArgument)
        tabCounter ++
        tabView.currentIndex = tabView.count() - 1 // 새로 추가된 탭 선택
    }

    // 초기 탭 추가
    Component.onCompleted: {
        addNewTab()
        addNewTab()
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 옵션 변경 컨트롤 (예시)
        RowLayout {
            Layout.fillWidth: true
            Layout.margins: 10
            spacing: 15
            FluLabel { text: "탭 너비 동작:" }
            FluComboBox {
                id: widthBehaviorCombo
                model: ["Equal", "SizeToContent", "Compact"]
                onCurrentIndexChanged: {
                    if (currentIndex === 0) tabView.tabWidthBehavior = FluTabViewType.Equal
                    else if (currentIndex === 1) tabView.tabWidthBehavior = FluTabViewType.SizeToContent
                    else tabView.tabWidthBehavior = FluTabViewType.Compact
                }
            }
            FluLabel { text: "닫기 버튼:" }
            FluComboBox {
                id: closeButtonCombo
                model: ["Always", "OnHover", "Never"]
                currentIndex: 0 // Always가 기본값
                onCurrentIndexChanged: {
                    if (currentIndex === 0) tabView.closeButtonVisibility = FluTabViewType.Always
                    else if (currentIndex === 1) tabView.closeButtonVisibility = FluTabViewType.OnHover
                    else tabView.closeButtonVisibility = FluTabViewType.Never
                }
            }
        }

        // FluTabView
        FluTabView {
            id: tabView
            Layout.fillWidth: true
            Layout.fillHeight: true

            // 새 탭 버튼 클릭 시
            onNewPressed: {
                addNewTab()
            }
        }
    }
}
```

### 참고 사항

*   **탭 콘텐츠 로딩**: 각 탭의 내용은 해당 탭이 활성화될 때 `FluLoader`를 통해 동적으로 로드됩니다. 따라서 `page` 프로퍼티는 반드시 인스턴스가 아닌 `Component` 타입이어야 합니다.
*   **데이터 전달**: `argument` 프로퍼티를 사용하여 탭별로 고유한 데이터를 해당 콘텐츠 컴포넌트에 전달할 수 있습니다. 콘텐츠 컴포넌트 내에서는 `argument`라는 이름의 프로퍼티로 이 데이터에 접근합니다.
*   **탭 조작**: 사용자는 탭을 드래그하여 순서를 변경할 수 있습니다. 닫기 버튼을 클릭하면 해당 탭이 모델에서 제거됩니다. '새 탭' 버튼은 `newPressed` 시그널을 발생시키며, 이 시그널 핸들러에서 `appendTab` 메소드를 호출하여 새 탭을 추가하는 로직을 구현해야 합니다.
*   **커스터마이징**: `tabWidthBehavior`, `closeButtonVisibility`, `itemWidth`, `addButtonVisibility` 프로퍼티를 사용하여 탭 뷰의 모양과 동작을 조절할 수 있습니다.
*   **스크롤**: 탭의 개수가 많아 헤더 영역의 너비를 초과할 경우, 내부 `ListView`는 자동으로 스크롤 기능을 제공하며 마우스 휠 스크롤도 지원합니다. 