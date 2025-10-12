# Fluent UI 레이아웃 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 특수한 목적의 레이아웃 컴포넌트들에 대해 설명합니다. 이 컴포넌트들은 복잡한 UI 구조를 효과적으로 구성하는 데 도움을 줍니다.

## 공통 임포트 방법

Fluent UI 레이아웃 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
// 필요에 따라 QtQuick.Layouts 등 추가 임포트
import QtQuick.Layouts 1.15 
```

---

## FluStaggeredLayout

`FluStaggeredLayout`은 높이가 가변적인 여러 아이템들을 효율적으로 배치하기 위한 '폭포수' 또는 '지그재그' 스타일의 레이아웃입니다. 아이템들은 가로 방향으로 배치될 수 있는 열(Column)들에 순서대로 추가되며, 항상 현재 가장 높이가 낮은 열에 배치됩니다. 이를 통해 아이템 간의 수직 공간 낭비를 최소화하고 시각적으로 흥미로운 배치를 만들 수 있습니다.

### 기반 클래스

`Item` (내부적으로 `Repeater`를 사용하여 모델 데이터 처리)

### 고유/특징적 프로퍼티

| 이름         | 타입        | 기본값 | 설명                                                                                                 |
| :----------- | :---------- | :----- | :--------------------------------------------------------------------------------------------------- |
| `itemWidth`  | `int`       | `200`  | 레이아웃 내 각 아이템의 고정 너비. 이 값과 레이아웃 전체 너비에 따라 자동으로 열 개수가 계산됩니다.                 |
| `model`      | `alias`     | -      | 표시할 데이터 모델. `Repeater`의 `model` 프로퍼티에 대한 별칭입니다. `ListModel` 또는 JavaScript 배열 등을 사용합니다. |
| `delegate`   | `alias`     | -      | 모델의 각 아이템을 표시할 QML 컴포넌트. `Repeater`의 `delegate` 프로퍼티에 대한 별칭입니다. 델리게이트는 반드시 `height`를 지정해야 합니다. | 
| `rowSpacing` | `int`       | `8`    | 아이템들 사이의 수평 간격 (열 간 간격).                                                                |
| `colSpacing` | `int`       | `8`    | 아이템들 사이의 수직 간격 (행 간 간격).                                                                |

### 고유 메소드

| 이름      | 파라미터 | 반환타입 | 설명                                                                       |
| :-------- | :------- | :------- | :------------------------------------------------------------------------- |
| `clear()` | 없음     | `void`   | 현재 레이아웃에 배치된 모든 아이템과 모델 데이터를 제거하고 레이아웃 상태를 초기화합니다. |
| `refresh()` | 없음     | `void`   | 현재 아이템들을 기준으로 레이아웃을 다시 계산하고 배치합니다. 주로 컨테이너 크기 변경 시 내부적으로 호출됩니다. | 

### 고유 시그널

`FluStaggeredLayout` 자체에 고유한 시그널은 정의되어 있지 않습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

FluContentPage {
    ListModel {
        id: myModel
        Component.onCompleted: {
            for(var i=0; i<20; ++i) {
                append({ color: Qt.hsla(Math.random(), 0.7, 0.6, 1.0), height: 100 + Math.random() * 150 });
            }
        }
    }

    Flickable {
        id: flickArea
        anchors.fill: parent
        contentHeight: layout.implicitHeight
        clip: true
        ScrollBar.vertical: FluScrollBar {}

        FluStaggeredLayout {
            id: layout
            width: flickArea.width // Flickable 너비에 맞춤
            model: myModel
            itemWidth: 180 // 각 아이템 너비
            rowSpacing: 10 // 수평 간격
            colSpacing: 10 // 수직 간격

            delegate: Rectangle {
                // 주의: delegate는 반드시 height를 가져야 함
                height: model.height // 모델 데이터에서 높이 가져오기
                color: model.color   // 모델 데이터에서 색상 가져오기
                radius: 4
                border.color: Qt.darker(color)

                FluText {
                    text: index
                    anchors.centerIn: parent
                    color: "white"
                    font.pixelSize: 20
                }
            }
        }
    }
}
```

### 참고 사항

*   **델리게이트 높이**: `delegate`로 지정된 컴포넌트는 반드시 명시적인 `height` 값을 가져야 레이아웃 계산이 가능합니다. 이 높이는 모델 데이터에 바인딩되거나 고정 값일 수 있습니다.
*   **동적 레이아웃**: `FluStaggeredLayout`의 너비가 변경되면 자동으로 열(column) 개수를 다시 계산하고 아이템들을 재배치합니다.
*   **성능**: 많은 수의 아이템을 처리할 때는 `Flickable`과 함께 사용하여 화면에 보이는 부분만 렌더링하는 것이 좋습니다.

--- 

## FluStatusLayout

`FluStatusLayout`은 데이터 로딩 상태나 조건에 따라 다른 뷰(로딩 중, 데이터 없음, 오류 발생, 성공)를 표시해주는 특수한 컨테이너 레이아웃입니다. 비동기 작업의 상태를 사용자에게 효과적으로 전달하는 데 유용합니다.

### 기반 클래스

`Item`

### 고유/특징적 프로퍼티

| 이름              | 타입        | 기본값                  | 설명                                                                                                                                 |
| :---------------- | :---------- | :---------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| `statusMode`      | `enum`      | `FluStatusLayoutType.Loading` | 현재 레이아웃의 상태를 나타냅니다. `FluStatusLayoutType` 열거형 값 (`Loading`, `Empty`, `Error`, `Success`) 중 하나를 사용합니다. 이 값에 따라 표시되는 뷰가 결정됩니다. | 
| `content`         | `default alias` | -                       | `statusMode`가 `Success`일 때 표시될 주 콘텐츠 아이템들을 배치하는 기본 프로퍼티 별칭.                                                     |
| `loadingText`     | `string`    | `qsTr("Loading...")`     | `statusMode`가 `Loading`일 때 표시될 텍스트.                                                                                          |
| `emptyText`       | `string`    | `qsTr("Empty")`         | `statusMode`가 `Empty`일 때 표시될 텍스트.                                                                                            |
| `errorText`       | `string`    | `qsTr("Error")`         | `statusMode`가 `Error`일 때 표시될 텍스트.                                                                                            |
| `errorButtonText` | `string`    | `qsTr("Reload")`      | `statusMode`가 `Error`일 때 표시될 버튼의 텍스트.                                                                                     |
| `color`           | `color`     | `Qt.rgba(0,0,0,0)`      | 로딩, 비어있음, 오류 상태 뷰의 배경색. 기본값은 투명입니다.                                                                               |
| `loadingItem`     | `Component` | (기본 로딩 뷰)          | `statusMode`가 `Loading`일 때 표시될 사용자 정의 컴포넌트. 지정하지 않으면 기본 로딩 뷰(진행 링 + 텍스트)가 표시됩니다.                               |
| `emptyItem`       | `Component` | (기본 비어있음 뷰)      | `statusMode`가 `Empty`일 때 표시될 사용자 정의 컴포넌트. 지정하지 않으면 기본 뷰(텍스트)가 표시됩니다.                                         |
| `errorItem`       | `Component` | (기본 오류 뷰)          | `statusMode`가 `Error`일 때 표시될 사용자 정의 컴포넌트. 지정하지 않으면 기본 뷰(텍스트 + 버튼)가 표시됩니다.                                   |

### 고유 메소드

| 이름                | 파라미터 | 반환타입 | 설명                                    |
| :------------------ | :------- | :------- | :-------------------------------------- |
| `showSuccessView()` | 없음     | `void`   | `statusMode`를 `Success`로 변경합니다.   |
| `showLoadingView()` | 없음     | `void`   | `statusMode`를 `Loading`으로 변경합니다.   |
| `showEmptyView()`   | 없음     | `void`   | `statusMode`를 `Empty`로 변경합니다.     |
| `showErrorView()`   | 없음     | `void`   | `statusMode`를 `Error`로 변경합니다.     |

### 고유 시그널

| 이름            | 파라미터 | 반환타입 | 설명                                                         |
| :-------------- | :------- | :------- | :----------------------------------------------------------- |
| `errorClicked()`| 없음     | -        | `statusMode`가 `Error`일 때 표시되는 기본 오류 뷰의 버튼을 클릭하면 발생합니다. | 

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

FluScrollablePage {
    FluFrame {
        Layout.fillWidth: true
        Layout.preferredHeight: 50
        RowLayout {
            FluDropDownButton {
                id: statusSelector
                text: "Loading"
                items: ["Loading", "Empty", "Error", "Success"]
                onCurrentTextChanged: {
                    if(currentText === "Loading") statusLayout.showLoadingView()
                    else if(currentText === "Empty") statusLayout.showEmptyView()
                    else if(currentText === "Error") statusLayout.showErrorView()
                    else if(currentText === "Success") statusLayout.showSuccessView()
                }
            }
        }
    }

    FluStatusLayout {
        id: statusLayout
        anchors.fill: parent
        anchors.topMargin: 60 // 버튼 영역 제외
        
        // 기본 상태는 Loading
        statusMode: FluStatusLayoutType.Loading 
        
        // 오류 상태에서 'Reload' 버튼 클릭 시 다시 로딩 시작
        onErrorClicked: {
            console.log("Reload button clicked!")
            statusLayout.showLoadingView()
            // 여기서 실제 데이터 로딩 로직 재시도
            timer.start() // 예시 타이머
        }
        
        // content (Success 상태일 때 보일 내용)
        Rectangle {
            color: FluColors.Green.normal
            anchors.fill: parent
            FluText {
                text: "데이터 로딩 성공!"
                anchors.centerIn: parent
                color: "white"
                font.pixelSize: 24
            }
        }
        
        // 예시: 2초 후 성공 상태로 변경하는 타이머
        Timer {
            id: timer
            interval: 2000
            onTriggered: statusLayout.showSuccessView()
            Component.onCompleted: start()
        }
    }
}
```

### 참고 사항

*   **상태 관리**: `statusMode` 프로퍼티를 변경하거나 `show...View()` 메소드를 호출하여 표시되는 뷰를 제어합니다.
*   **콘텐츠 표시**: 실제 보여주고자 하는 주 콘텐츠는 `FluStatusLayout { ... }` 블록 내부에 직접 배치하여 `content` (기본 프로퍼티)에 할당합니다. 이 콘텐츠는 `statusMode`가 `Success`일 때만 보입니다.
*   **상태 뷰 커스터마이징**: `loadingText`, `emptyText` 등의 프로퍼티로 기본 상태 뷰의 텍스트를 변경하거나, `loadingItem`, `emptyItem`, `errorItem` 프로퍼티에 사용자 정의 QML `Component`를 지정하여 각 상태 뷰의 전체 UI를 완전히 변경할 수 있습니다.
*   **오류 처리**: `onErrorClicked` 시그널을 사용하여 오류 상태에서 사용자가 재시도 버튼을 눌렀을 때의 동작(예: 데이터 다시 불러오기)을 구현할 수 있습니다.

--- 

## FluSplitLayout

`FluSplitLayout`은 두 개 이상의 아이템을 가로나 세로로 배치하고, 그 사이에 크기 조절이 가능한 핸들(구분선)을 제공하는 레이아웃입니다. 사용자는 이 핸들을 드래그하여 각 아이템이 차지하는 공간의 비율을 동적으로 변경할 수 있습니다. `QtQuick.Controls.SplitView`를 기반으로 하며 핸들의 시각적 스타일만 Fluent UI에 맞게 변경되었습니다.

### 기반 클래스

`QtQuick.Controls.SplitView`

### 주요 상속 프로퍼티

`FluSplitLayout`은 `SplitView`의 모든 프로퍼티를 상속받습니다. 주요 프로퍼티는 다음과 같습니다:

*   `orientation`: 분할 방향. `Qt.Horizontal` (기본값) 또는 `Qt.Vertical`.
*   아이템 배치: `FluSplitLayout`의 자식으로 배치된 아이템들이 분할된 영역에 표시됩니다.
*   `handle`: 구분선 핸들의 모양과 동작을 정의하는 프로퍼티.
*   `SplitView`의 Attached Properties: 자식 아이템에서 `SplitView.minimumWidth`, `SplitView.maximumWidth`, `SplitView.fillWidth` 등을 사용하여 크기 제약 및 자동 크기 조절 동작을 설정할 수 있습니다 (세로 방향일 경우 `Height` 사용).

### 고유/스타일링 프로퍼티

| 이름          | 타입    | 기본값      | 설명                                             |
| :------------ | :------ | :---------- | :----------------------------------------------- |
| `handleColor` | `color` | (테마 기반) | 구분선 핸들 중앙에 표시되는 작은 막대의 색상입니다. |

### 고유 시그널 / 메소드

`SplitView`에서 상속된 시그널과 메소드를 그대로 사용합니다 (예: `handleMoved` 시그널).

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

FluContentPage {

    FluSplitLayout {
        id: splitLayout
        anchors.fill: parent
        orientation: Qt.Horizontal // 가로 분할 (기본값)

        // 첫 번째 영역
        Rectangle {
            color: FluColors.Blue.light
            implicitWidth: 150 // 초기 너비
            SplitView.minimumWidth: 100 // 최소 너비
            SplitView.maximumWidth: 300 // 최대 너비
            FluText { anchors.centerIn: parent; text: "영역 1" }
        }

        // 두 번째 영역 (자동 채움)
        Rectangle {
            color: FluColors.Teal.light
            SplitView.fillWidth: true // 남은 공간 채우기
            SplitView.minimumWidth: 200
            FluText { anchors.centerIn: parent; text: "영역 2" }
        }

        // 세 번째 영역
        Rectangle {
            color: FluColors.Green.light
            implicitWidth: 150
            SplitView.minimumWidth: 100
             FluText { anchors.centerIn: parent; text: "영역 3" }
        }
    }
    
    // 방향 전환 버튼 (예시)
    FluButton {
        anchors { right: parent.right; top: parent.top; margins: 10 }
        text: splitLayout.orientation === Qt.Horizontal ? "세로로 변경" : "가로로 변경"
        onClicked: {
            splitLayout.orientation = (splitLayout.orientation === Qt.Horizontal ? Qt.Vertical : Qt.Horizontal)
        }
    }
}
```

### 참고 사항

*   **기본 기능**: `FluSplitLayout`은 `QtQuick.Controls.SplitView`와 기능적으로 동일합니다. 자식 아이템들을 배치하고 필요에 따라 `SplitView`의 Attached Properties를 사용하여 크기 조절 동작을 정의합니다.
*   **핸들 스타일**: 구분선 핸들의 모양(두께, 호버/클릭 시 배경색, 중앙 막대)이 Fluent UI 스타일에 맞게 기본 제공됩니다. `handleColor` 프로퍼티로 중앙 막대의 색상을 변경할 수 있습니다.
