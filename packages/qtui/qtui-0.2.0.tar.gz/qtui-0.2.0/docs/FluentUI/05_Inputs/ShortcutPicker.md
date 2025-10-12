# Fluent UI 단축키 선택 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluShortcutPicker` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 사용자가 키보드 단축키를 보고 편집할 수 있는 인터페이스를 제공합니다.

## 공통 임포트 방법

Fluent UI 단축키 선택 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluShortcutPicker

현재 설정된 키보드 단축키 조합을 시각적으로 표시하고, 편집 아이콘이 포함된 버튼 형태로 제공됩니다. `FluIconButton`을 기반으로 하며, 버튼 클릭 시 나타나는 대화 상자를 통해 사용자가 새로운 키 조합을 눌러 단축키를 변경할 수 있습니다. 또한, 설정된 단축키가 시스템의 다른 단축키와 충돌하는 경우 "Conflict"라는 텍스트를 표시하여 사용자에게 알릴 수 있습니다.

### 주요 상속 프로퍼티 (FluIconButton)

`FluShortcutPicker`는 `FluIconButton`의 기본적인 시각적 스타일(배경색, 테두리 등) 및 상호작용 상태(호버, 누름 등)와 관련된 프로퍼티를 상속받습니다. 그러나 주 기능은 단축키 표시에 맞춰져 있습니다.

### 고유/특징적 프로퍼티

| 이름           | 타입         | 기본값                             | 설명                                                                                                |
| :------------- | :----------- | :--------------------------------- | :-------------------------------------------------------------------------------------------------- |
| `current`      | `var`        | `["Ctrl","Shift","A"]`           | 현재 설정된 단축키 키 조합 (문자열 배열). 예: `["Alt", "F4"]`.                                               |
| `title`        | `string`     | `qsTr("Activate the Shortcut")`  | 팝업 대화 상자의 제목 텍스트.                                                                           |
| `message`      | `string`     | `qsTr("Press the key combination...")` | 팝업 대화 상자 본문에 표시될 안내 메시지.                                                                  |
| `positiveText` | `string`     | `qsTr("Save")`                   | 팝업 대화 상자의 '저장' (긍정) 버튼 텍스트.                                                                |
| `neutralText`  | `string`     | `qsTr("Cancel")`                 | 팝업 대화 상자의 '취소' (중립) 버튼 텍스트. 편집 내용을 저장하지 않고 닫습니다.                                 |
| `negativeText` | `string`     | `qsTr("Reset")`                  | 팝업 대화 상자의 '리셋' (부정) 버튼 텍스트. 팝업 열기 전의 값으로 되돌리고 닫습니다.                              |
| `registered`   | `bool`       | `true`                             | 단축키가 시스템에 성공적으로 등록되었는지 (다른 단축키와 충돌하지 않는지) 여부. `false`이면 "Conflict" 메시지가 표시됩니다. |
| `errorColor`   | `color`      | `Qt.rgba(250/255,85/255,85/255,1)` | `registered`가 `false`일 때 표시되는 "Conflict" 텍스트의 색상.                                               |
| `syncHotkey`   | `FluHotkey`  | `undefined`                        | 동기화할 `FluHotkey` 객체. 이 프로퍼티를 설정하면 `FluShortcutPicker`의 `current`와 `registered`가 해당 `FluHotkey`의 `sequence` 및 `isRegistered`와 자동으로 연동됩니다. | 

### 고유 시그널

| 이름        | 파라미터 | 반환타입 | 설명                                                     |
| :---------- | :------- | :------- | :------------------------------------------------------- |
| `accepted()`| 없음     | -        | 사용자가 팝업 대화 상자에서 '저장'(positive) 버튼을 눌렀을 때 발생. | 

### 예제

```qml
import QtQuick 2.15
import FluentUI 1.0
import QtQuick.Layouts 1.15

ColumnLayout {
    spacing: 10

    // 가상의 FluHotkey 객체 (실제 사용 시에는 적절히 생성 또는 참조)
    FluHotkey {
        id: myHotkey
        name: "Open File Hotkey"
        sequence: "Ctrl+O"
    }

    FluShortcutPicker {
        id: shortcutPicker
        text: qsTr("파일 열기 단축키:") // Picker 앞에 표시될 레이블
        syncHotkey: myHotkey // FluHotkey 객체와 동기화
        Layout.preferredWidth: 300

        onAccepted: {
            console.log("단축키 저장됨:", current.join('+'))
            // 필요한 경우 여기서 추가 로직 수행 (예: 설정 저장)
        }
    }

    FluText {
        // 동기화된 Hotkey의 현재 시퀀스를 보여주는 예시
        text: qsTr("연결된 Hotkey 시퀀스: %1").arg(myHotkey.sequence)
    }
    FluText {
        // Hotkey 등록 상태 표시 예시
        text: qsTr("등록 상태: %1").arg(myHotkey.isRegistered ? "성공" : "충돌/실패")
        color: myHotkey.isRegistered ? "green" : "red"
    }
}
```

### 참고 사항

*   `current` 프로퍼티는 키 이름을 문자열로 가지는 JavaScript 배열입니다. (예: `["Ctrl", "Shift", "A"]`)
*   팝업 대화 상자가 열리면 키보드 입력이 활성화됩니다. 사용자가 키 조합(예: Ctrl+Shift+P)을 누르면 해당 키들이 인식되어 표시됩니다. 지원되는 키 이름은 내부 `keyToString` 함수에 정의되어 있습니다.
*   `syncHotkey` 프로퍼티를 사용하면 `FluHotkey` 컴포넌트와 쉽게 연동하여 단축키 설정 및 상태 관리를 통합할 수 있습니다. `accepted` 시그널 발생 시 `syncHotkey`의 `sequence`가 자동으로 업데이트됩니다.
*   `registered` 프로퍼티는 주로 `syncHotkey`과 연동될 때 그 상태를 반영하여 UI에 충돌 여부를 표시하는 데 사용됩니다.
*   팝업 대화 상자의 버튼(`positiveText`, `neutralText`, `negativeText`) 텍스트는 필요에 따라 사용자 정의할 수 있습니다. 