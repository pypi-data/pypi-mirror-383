# Fluent UI 페이지 (FluPage)

이 문서에서는 `FluentUI` 모듈의 핵심 컨테이너 컴포넌트 중 하나인 `FluPage`에 대해 설명합니다. `FluPage`는 애플리케이션 내의 개별 화면 또는 뷰를 구성하는 기본 단위이며, 특히 `FluNavigationView`와 함께 사용될 때 페이지 전환 및 관리를 담당합니다.

`FluPage`는 Qt Quick Controls의 `Page`를 기반으로 하며, Fluent UI 스타일의 애니메이션과 기본적인 헤더 구조를 추가로 제공합니다.

## 공통 임포트 방법

`FluPage`를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0
```

---

## FluPage

`FluPage`는 애플리케이션의 특정 기능 또는 콘텐츠 영역을 나타내는 화면 단위입니다. `FluNavigationView`의 스택(Stack)에 추가되어 관리되며, 페이지가 표시될 때 부드러운 애니메이션 효과(아래에서 위로 나타나며 투명도 조절)와 함께 나타납니다. 페이지 제목(`title`)이 설정된 경우, 기본적으로 상단에 해당 제목을 표시하는 헤더 영역이 포함됩니다.

### 기반 클래스

`QtQuick.Controls.Page`

### 주요 프로퍼티

| 이름             | 타입   | 기본값                   | 설명                                                                                                                                                            |
| :--------------- | :----- | :----------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `launchMode`     | `enum` | `FluPageType.SingleTop`  | `FluNavigationView`에서 페이지가 스택에 추가될 때의 동작 방식을 지정합니다 (`FluPageType` 열거형 값 사용). 예를 들어 `SingleTop`은 동일 URL 페이지가 이미 스택 상단에 있으면 새로 추가하지 않고 기존 것을 사용합니다. |
| `animationEnabled` | `bool` | `FluTheme.animationEnabled` | 페이지가 나타날 때 애니메이션 효과(Translate Y, Opacity)를 사용할지 여부입니다. 기본적으로 전역 테마 설정을 따릅니다.                                                              |
| `url`            | `string` | `""`                   | 페이지를 고유하게 식별하거나 `FluRouter`와 연동할 때 사용될 수 있는 URL 경로입니다.                                                                                  |
| `padding`        | `real` | `5`                      | 페이지 내용 영역의 안쪽 여백입니다. (상속됨)                                                                                                                    |
| `title`          | `string` | `""`                   | 페이지의 제목입니다. 이 값이 설정되면 기본 헤더(`header`)에 해당 제목이 `FluText` (스타일: `FluTextStyle.Title`)로 표시됩니다. (상속됨)                                      |
| `header`         | `Item` | (기본 헤더 컴포넌트 제공)  | 페이지 상단에 표시될 아이템입니다. 기본적으로 `title`을 표시하는 `FluText`를 포함하며, `title`이 비어있으면 표시되지 않습니다. 커스텀 헤더로 교체할 수 있습니다. (상속됨)          |
| `background`     | `Item` | (빈 Item 제공)           | 페이지의 배경 아이템입니다. 기본적으로 비어 있으며, 필요시 커스텀 배경을 지정할 수 있습니다. (상속됨)                                                                           |

*(이 외 `Page`로부터 `contentItem`, `implicitWidth`, `implicitHeight` 등 다수의 프로퍼티 및 시그널 상속)*

### 주요 시그널

`Page` 및 `Item`으로부터 상속받는 표준 시그널 외에, `StackView`와 관련된 중요한 시그널 핸들러가 있습니다.

| 이름              | 파라미터 | 반환타입 | 설명                                                                      |
| :---------------- | :------- | :------- | :------------------------------------------------------------------------ |
| `StackView.onRemoved` | 없음     | -        | 페이지가 `FluNavigationView`의 스택에서 제거될 때 호출됩니다. 기본적으로 `destroy()`가 연결되어 페이지 객체를 메모리에서 해제합니다. |

### 주요 특징 및 동작

*   **애니메이션**: 페이지가 `Component.onCompleted` 시점에 `visible`이 `true`로 설정되면서, `transform`의 Y축 이동과 `opacity` 변경 애니메이션이 동시에 실행되어 부드럽게 나타나는 효과를 줍니다.
*   **자동 소멸**: `StackView.onRemoved` 시그널에 `destroy()`가 연결되어 있어, 네비게이션 스택에서 페이지가 제거되면(예: 뒤로 가기) 해당 페이지 인스턴스는 자동으로 소멸됩니다. 이는 메모리 관리에 도움이 됩니다.
*   **기본 헤더**: `title` 프로퍼티가 설정되어 있으면 자동으로 페이지 상단에 제목을 표시하는 헤더가 생성됩니다. (`implicitHeight: 40`)

---

## 예제

다음은 간단한 `FluPage` 사용 예시입니다.

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

FluPage {
    // 네비게이션 라우터 등에서 사용할 페이지 식별자 (선택 사항)
    url: "/mySimplePage"
    
    // 페이지 제목 설정 (자동으로 헤더에 표시됨)
    title: qsTr("간단한 페이지")
    
    // 페이지 내용 영역 안쪽 여백 설정
    padding: 20
    
    // 페이지 내용 정의 (contentItem에 해당)
    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        
        FluText {
            text: qsTr("이것은 FluPage의 내용입니다.")
            Layout.fillWidth: true
        }
        
        FluButton {
            text: qsTr("버튼")
        }
    }
    
    // 커스텀 헤더 사용 예시 (기본 헤더 대신 사용)
    /*
    header: Item {
        implicitHeight: 50
        Rectangle { anchors.fill: parent; color: "lightblue" }
        FluText { text: "나만의 커스텀 헤더"; anchors.centerIn: parent }
    }
    */
}
```

---

## 참고 사항

*   `FluPage`는 일반적으로 단독으로 사용되기보다는 `FluNavigationView` 내부에 동적으로 로드되어 사용됩니다. `FluNavigationView`는 `FluPage`의 `launchMode`를 해석하고 스택 관리를 수행합니다.
*   페이지 전환 애니메이션은 `FluTheme.animationEnabled` 및 `FluPage` 자체의 `animationEnabled` 프로퍼티에 의해 제어됩니다.
*   페이지가 스택에서 제거될 때 상태를 저장하거나 특별한 정리 작업이 필요하다면, `StackView.onRemoved` 핸들러를 재정의하여 `destroy()` 호출 전에 해당 로직을 추가할 수 있습니다. 하지만 대부분의 경우 기본 자동 소멸 동작으로 충분합니다.
*   `title`만 설정하면 간단한 헤더가 자동으로 생성되지만, 더 복잡한 헤더 UI가 필요하다면 `header` 프로퍼티에 커스텀 `Item`을 직접 할당하여 구현할 수 있습니다.

---

## FluScrollablePage

`FluScrollablePage`는 `FluPage`를 확장하여 콘텐츠 영역이 페이지 높이를 초과할 경우 자동으로 수직 스크롤 기능을 제공하는 페이지 컴포넌트입니다. 내부적으로 `Flickable`과 `FluScrollBar`를 사용하여 스크롤 기능을 구현하며, 콘텐츠는 `ColumnLayout` 안에 배치됩니다.

### 기반 클래스

`FluPage`

### 주요 특징 및 동작

*   **자동 스크롤**: 페이지에 추가된 자식 아이템들의 전체 높이가 페이지의 가시 영역 높이보다 클 경우, 자동으로 수직 스크롤바(`FluScrollBar`)가 나타나며 사용자는 마우스 휠이나 스크롤바를 드래그하여 콘텐츠를 스크롤할 수 있습니다.
*   **내부 구조**: `FluPage` 내부에 `Flickable` 아이템이 `anchors.fill`로 채워지고, 이 `Flickable` 내부에 `ColumnLayout` (id: `container`)이 배치됩니다. 개발자가 `FluScrollablePage` 태그 내에 직접 추가하는 자식 아이템들은 이 `ColumnLayout`의 자식으로 추가됩니다.
*   **기본 프로퍼티 (`content`)**: `FluScrollablePage`의 기본 프로퍼티는 `content`이며, 이는 내부 `ColumnLayout`의 `data` 프로퍼티에 대한 별칭(`alias`)입니다. 따라서 QML에서 자식 아이템들을 `<FluScrollablePage>` 태그 내부에 직접 정의하면 자동으로 `ColumnLayout`에 추가됩니다.

### 주요 프로퍼티

| 이름      | 타입       | 기본값                  | 설명                                                                                             |
| :-------- | :--------- | :---------------------- | :----------------------------------------------------------------------------------------------- |
| `content` | `alias`    | (내부 `container.data`) | 기본 프로퍼티. 페이지의 스크롤 가능한 콘텐츠 영역에 추가될 자식 아이템들의 리스트입니다. 내부 `ColumnLayout`의 `data`에 연결됩니다. |

*(이 외 `FluPage`의 모든 프로퍼티, 메소드, 시그널 상속. 예: `title`, `launchMode`, `padding` 등)*

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

FluScrollablePage {
    title: qsTr("스크롤 가능 페이지")
    padding: 15 // 페이지 전체의 패딩
    
    // FluScrollablePage의 기본 프로퍼티(content)에 아이템들이 추가됨
    // 아이템들은 내부 ColumnLayout에 의해 수직으로 배치됨
    
    FluText {
        text: qsTr("페이지 상단 내용")
        font: FluTextStyle.Subtitle
        Layout.bottomMargin: 10
    }
    
    Repeater {
        model: 20 // 많은 아이템 생성하여 스크롤 발생시키기
        delegate: FluFrame {
            Layout.fillWidth: true
            height: 80
            padding: 10
            Layout.bottomMargin: 10
            
            FluText {
                text: qsTr("아이템 %1").arg(index + 1)
                anchors.centerIn: parent
            }
        }
    }
    
    FluText {
        text: qsTr("페이지 하단 내용")
        font: FluTextStyle.Subtitle
        Layout.topMargin: 10
    }
}
```

### 참고 사항

*   `FluScrollablePage`는 콘텐츠가 많아 한 화면에 다 들어오지 않을 가능성이 있는 페이지를 만들 때 유용합니다.
*   기본적으로 수직 스크롤만 지원합니다. 수평 스크롤이 필요하면 `Flickable`의 `contentWidth`를 설정하고 수평 스크롤바를 추가하는 등 직접 구현해야 합니다.
*   내부 `Flickable`의 `clip` 프로퍼티는 `true`로 설정되어 있어 콘텐츠가 페이지 영역 밖으로 벗어나지 않습니다.
*   내부 `ColumnLayout`을 사용하므로, 자식 아이템들은 자동으로 수직 정렬됩니다. 레이아웃 관련 프로퍼티(예: `Layout.fillWidth`, `Layout.preferredHeight`)를 사용하여 각 아이템의 크기와 배치를 조절할 수 있습니다. 