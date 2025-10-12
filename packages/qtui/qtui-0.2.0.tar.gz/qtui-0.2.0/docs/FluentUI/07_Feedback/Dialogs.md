# Fluent UI 대화 상자 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 대화 상자 관련 컴포넌트인 `FluContentDialog`와 `FluWindowDialog`에 대해 설명합니다.

## 공통 임포트 방법

Fluent UI 대화 상자 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
// 필요에 따라 Window, Layouts 등 추가
import QtQuick.Window 2.15
import QtQuick.Layouts 1.15 
```

---

## FluContentDialog

`FluContentDialog`는 현재 창 위에 표시되는 모달(modal) 팝업 형태의 대화 상자입니다. 사용자에게 중요한 정보를 알리거나, 간단한 결정(예: 확인/취소)을 요구할 때 사용됩니다. 제목, 메시지 텍스트, 선택적인 사용자 정의 콘텐츠 영역, 그리고 하단의 버튼 영역으로 구성됩니다. `FluPopup`을 기반으로 구현되었습니다.

### 기반 클래스

`FluPopup`

### 고유/특징적 프로퍼티

| 이름                    | 타입        | 기본값                                      | 설명                                                                                                                                           |
| :---------------------- | :---------- | :------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| `title`                 | `string`    | `""`                                        | 대화 상자 상단에 표시될 제목 텍스트.                                                                                                          |
| `message`               | `string`    | `""`                                        | 제목 아래에 표시될 주 내용 메시지. 긴 텍스트는 자동으로 스크롤 가능한 영역 안에 표시될 수 있습니다.                                                         |
| `neutralText`           | `string`    | `qsTr("Close")`                           | 중립(Neutral) 버튼에 표시될 텍스트.                                                                                                       |
| `negativeText`          | `string`    | `qsTr("Cancel")`                          | 부정(Negative) 버튼 (일반적으로 '취소')에 표시될 텍스트.                                                                                         |
| `positiveText`          | `string`    | `qsTr("OK")`                              | 긍정(Positive) 버튼 (일반적으로 '확인')에 표시될 텍스트.                                                                                         |
| `buttonFlags`           | `int`       | `FluContentDialogType.NegativeButton | PositiveButton` | 표시할 버튼의 조합을 지정하는 플래그. `FluContentDialogType` 열거형 값 (`NeutralButton`, `NegativeButton`, `PositiveButton`)들의 비트 OR 조합을 사용합니다. | 
| `contentDelegate`       | `Component` | (빈 `Item`)                                 | 메시지와 버튼 영역 사이에 표시될 사용자 정의 QML 컴포넌트. 복잡한 UI 요소를 대화 상자 내에 포함시킬 때 사용합니다.                                            |
| `onNeutralClickListener`| `var` (함수)| `undefined`                                 | 중립 버튼 클릭 시 호출될 사용자 정의 JavaScript 함수. 지정하면 기본 동작(시그널 발생 및 닫기) 대신 이 함수만 실행됩니다.                                           |
| `onNegativeClickListener`| `var` (함수)| `undefined`                                 | 부정 버튼 클릭 시 호출될 사용자 정의 JavaScript 함수. 지정하면 기본 동작 대신 이 함수만 실행됩니다.                                                         |
| `onPositiveClickListener`| `var` (함수)| `undefined`                                 | 긍정 버튼 클릭 시 호출될 사용자 정의 JavaScript 함수. 지정하면 기본 동작 대신 이 함수만 실행됩니다.                                                         |

*   `FluContentDialogType` 열거형은 `NeutralButton` (1), `NegativeButton` (2), `PositiveButton` (4) 값을 가집니다.

### 고유 시그널

| 이름             | 파라미터 | 반환타입 | 설명                                                                                             | 
| :--------------- | :------- | :------- | :----------------------------------------------------------------------------------------------- |
| `neutralClicked` | 없음     | -        | 중립 버튼이 클릭되었을 때 발생합니다 (해당 `on...Listener`가 설정되지 않은 경우). 기본적으로 대화 상자를 닫습니다. |
| `negativeClicked`| 없음     | -        | 부정 버튼이 클릭되었을 때 발생합니다 (해당 `on...Listener`가 설정되지 않은 경우). 기본적으로 대화 상자를 닫습니다. |
| `positiveClicked`| 없음     | -        | 긍정 버튼이 클릭되었을 때 발생합니다 (해당 `on...Listener`가 설정되지 않은 경우). 기본적으로 대화 상자를 닫습니다. |

### 고유 메소드

*   `open()`: 대화 상자를 표시합니다. (`FluPopup`에서 상속)
*   `close()`: 대화 상자를 닫습니다. (`FluPopup`에서 상속)

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    spacing: 15

    FluButton {
        text: qsTr("기본 확인/취소 대화상자")
        onClicked: dialog1.open()
    }

    FluButton {
        text: qsTr("3개 버튼 대화상자")
        onClicked: dialog2.open()
    }

    FluButton {
        text: qsTr("사용자 정의 콘텐츠 대화상자")
        onClicked: dialog3.open()
    }
}

// 기본 확인/취소 대화상자 정의
FluContentDialog {
    id: dialog1
    title: qsTr("알림")
    message: qsTr("작업을 계속하시겠습니까?")
    // buttonFlags 기본값 사용 (Negative + Positive)
    onNegativeClicked: console.log("취소됨")
    onPositiveClicked: console.log("확인됨")
}

// 3개 버튼 대화상자 정의
FluContentDialog {
    id: dialog2
    title: qsTr("저장되지 않은 변경 사항")
    message: qsTr("변경 사항을 저장하시겠습니까?")
    buttonFlags: FluContentDialogType.NeutralButton | FluContentDialogType.NegativeButton | FluContentDialogType.PositiveButton
    neutralText: qsTr("저장 안 함")
    negativeText: qsTr("취소")
    positiveText: qsTr("저장")
    onNeutralClicked: console.log("저장 안 함")
    onNegativeClicked: console.log("취소")
    onPositiveClicked: console.log("저장")
}

// 사용자 정의 콘텐츠 대화상자 정의
FluContentDialog {
    id: dialog3
    title: qsTr("처리 중")
    message: qsTr("데이터를 처리하고 있습니다. 잠시 기다려주세요...")
    buttonFlags: FluContentDialogType.NegativeButton // 취소 버튼만 표시
    negativeText: qsTr("중단")
    
    // contentDelegate를 사용하여 프로그레스 링 추가
    contentDelegate: Component {
        Item {
            implicitWidth: parent.width
            implicitHeight: 80
            FluProgressRing {
                anchors.centerIn: parent
                indeterminate: true
            }
        }
    }
    
    onNegativeClicked: {
        console.log("처리 중단됨")
        // 여기서 처리 중단 로직 수행
    }
}

```

### 참고 사항

*   **모달 동작**: `FluContentDialog`는 표시될 때 부모 창의 다른 UI 요소와의 상호작용을 차단하는 모달(modal) 방식으로 동작합니다.
*   **버튼 구성**: `buttonFlags` 프로퍼티에 `FluContentDialogType` 열거형 값들을 비트 OR 연산(`|`)으로 조합하여 원하는 버튼들만 표시할 수 있습니다.
*   **클릭 처리**: 버튼 클릭 시 기본적으로 해당 시그널(`neutralClicked` 등)이 발생하고 대화 상자가 닫힙니다. 만약 `on...ClickListener` 프로퍼티에 JavaScript 함수를 할당하면, 해당 함수만 실행되고 기본 동작(시그널 발생 및 닫기)은 수행되지 않습니다. 리스너 함수 내에서 `control.close()`를 명시적으로 호출하여 대화 상자를 닫을 수 있습니다.
*   **사용자 정의 콘텐츠**: `contentDelegate`에 `Component`를 지정하여 메시지와 버튼 영역 사이에 원하는 QML UI 요소를 자유롭게 추가할 수 있습니다. 추가된 콘텐츠의 크기에 맞춰 대화 상자 높이가 조절될 수 있습니다.

--- 

## FluWindowDialog

`FluWindowDialog`는 별도의 독립된 창(Window) 형태로 표시되는 대화 상자를 생성하는 데 사용됩니다. 주 애플리케이션 창과 분리된 컨텍스트를 가지며, 파일 선택, 설정 변경 등 더 복잡한 UI나 독립적인 동작이 필요한 경우에 적합합니다. `FluWindow`를 기반으로 구현되었습니다.

### 기반 클래스

`FluWindow`

### 고유/특징적 프로퍼티

| 이름              | 타입        | 기본값 | 설명                                                                                                         |
| :---------------- | :---------- | :----- | :----------------------------------------------------------------------------------------------------------- |
| `contentDelegate` | `Component` | -      | **필수**. 대화 상자 창 내부에 표시될 내용을 정의하는 QML 컴포넌트. 이 컴포넌트가 대화 상자의 UI를 구성합니다.                |
| `autoVisible`     | `bool`      | `false`| 컴포넌트 생성 시 자동으로 보이게 할지 여부. 일반적으로 `false`로 두고 `showDialog()` 메소드를 사용해 표시합니다. |
| `autoDestroy`     | `bool`      | `true` | 대화 상자 창이 닫힐 때(`visibility`가 `Hidden`으로 변경될 때) 컴포넌트 인스턴스를 자동으로 파괴할지 여부.              |
| `fixSize`         | `bool`      | `true` | 대화 상자 창의 크기를 고정할지 여부. `true`이면 사용자가 창 크기를 조절할 수 없습니다.                             |

*   `title`, `width`, `height`, `modality`, `flags` 등 `FluWindow`의 다른 프로퍼티들도 상속받아 사용할 수 있습니다.

### 고유 메소드

| 이름         | 파라미터                      | 반환타입 | 설명                                                                                                                                                           |
| :----------- | :---------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `showDialog` | `int`: `offsetX` (0), `int`: `offsetY` (0) | `void`   | 대화 상자 창을 표시합니다. 창은 기본적으로 부모 창(`transientParent`)의 중앙에 위치하며, `offsetX`와 `offsetY`를 통해 위치를 미세 조정할 수 있습니다. 부모 창의 `stayTop` 속성도 상속받습니다. | 

*   `close()`: 대화 상자 창을 닫습니다. (`FluWindow`에서 상속)
*   `closeListener`: 창 닫기 이벤트 발생 시 호출될 사용자 정의 JavaScript 함수를 지정할 수 있습니다.

### 고유 시그널

`FluWindow`에서 상속된 시그널(예: `visibilityChanged`, `closing` 등)을 사용할 수 있습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 600
    height: 400
    title: "FluWindowDialog 예제"

    FluButton {
        anchors.centerIn: parent
        text: "독립 창 대화상자 열기"
        onClicked: myWindowDialog.showDialog()
    }

    // FluWindowDialog 정의
    FluWindowDialog {
        id: myWindowDialog
        title: "설정" // 창 제목
        width: 300
        height: 200
        // fixSize: false // 크기 조절 가능하게 하려면
        // modality: Qt.ApplicationModal // 애플리케이션 모달로 설정하려면
        
        // contentDelegate: 대화 상자 내부 UI 정의
        contentDelegate: Component {
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 15
                spacing: 10

                FluText { text: "옵션 설정" }
                FluCheckBox { text: "자동 저장 활성화" }
                FluSlider { Layout.fillWidth: true }
                
                Item { Layout.fillHeight: true } // 공간 채우기
                
                RowLayout {
                    Layout.alignment: Qt.AlignRight
                    FluButton { 
                        text: "취소"
                        onClicked: myWindowDialog.close() // 창 닫기
                    }
                    FluFilledButton { 
                        text: "확인"
                        onClicked: { 
                            console.log("설정 확인됨")
                            myWindowDialog.close() // 창 닫기
                        }
                    }
                }
            }
        } // Component 끝
        
        // 창 닫기 시그널 핸들러 (예시)
        onClosing: {
            console.log("설정 창 닫힘")
        }
    } // FluWindowDialog 끝
}

```

### 참고 사항

*   **독립 창**: `FluContentDialog`와 달리 `FluWindowDialog`는 별도의 시스템 창으로 나타납니다.
*   **`contentDelegate`**: 대화 상자의 내용을 정의하는 핵심 요소입니다. `Component` 내부에 원하는 UI 구조를 자유롭게 구성할 수 있습니다.
*   **표시 및 위치**: `showDialog()` 메소드를 호출하여 대화 상자를 표시합니다. 기본적으로 부모 창의 중앙에 나타나며 `offsetX`, `offsetY`로 위치 조정이 가능합니다.
*   **자동 파괴**: `autoDestroy`가 `true`(기본값)이면 창이 닫힐 때 QML 컴포넌트 인스턴스도 메모리에서 제거됩니다. `false`로 설정하면 인스턴스가 유지되어 나중에 다시 `showDialog()`로 표시할 수 있습니다.
*   **부모 창 상호작용**: `modality` 프로퍼티(예: `Qt.WindowModal`, `Qt.ApplicationModal`)를 설정하여 부모 창과의 상호작용을 제어할 수 있습니다.

</rewritten_file> 