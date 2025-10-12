# Fluent UI 플립 뷰 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluFlipView` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 여러 항목을 한 번에 하나씩 보여주고, 이전/다음 버튼 또는 마우스 휠을 사용하여 항목 간을 탐색할 수 있게 해줍니다.

## 공통 임포트 방법

Fluent UI 플립 뷰 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
// 필요에 따라 Controls 등 추가
import QtQuick.Controls 2.15 
```

---

## FluFlipView

`FluFlipView`는 이미지 갤러리나 단계별 안내와 같이 순차적인 콘텐츠 모음을 표시하는 데 사용되는 컨트롤입니다. 사용자는 내장된 이전/다음 버튼을 클릭하거나 마우스 휠을 스크롤하여 컬렉션의 항목들을 하나씩 넘겨볼 수 있습니다. 수평(기본값) 또는 수직 방향으로 탐색 방향을 설정할 수 있습니다.

이 컴포넌트는 내부적으로 `QtQuick.Controls`의 `SwipeView`를 사용하지만, 사용자가 직접 콘텐츠를 드래그하여 스와이프하는 상호작용은 비활성화되어 있습니다. 오직 제공되는 버튼과 마우스 휠을 통해서만 탐색이 가능합니다.

### 기반 클래스

`Item` (내부적으로 `SwipeView` 포함)

### 고유/특징적 프로퍼티

| 이름         | 타입         | 기본값  | 설명                                                                                                                               |
| :----------- | :----------- | :------ | :--------------------------------------------------------------------------------------------------------------------------------- |
| `vertical`   | `bool`       | `false` | 플립 뷰의 방향을 설정합니다. `true`이면 항목이 수직으로 쌓이고 상하 버튼으로 탐색하며, `false`이면 수평으로 배열되고 좌우 버튼으로 탐색합니다. |
| `content`    | `default alias` (list<Item>) | `[]`    | 플립 뷰 내부에 표시될 자식 항목(Item)들의 리스트입니다. `SwipeView`의 `contentData` 프로퍼티에 대한 별칭입니다.                               |
| `currentIndex`| `alias` (int) | `0`     | 현재 화면에 표시된 항목의 인덱스(0부터 시작)입니다. 이 값을 읽거나 설정하여 현재 페이지를 확인하거나 변경할 수 있습니다. `SwipeView`의 `currentIndex`에 대한 별칭입니다. | 

### 고유 메소드

`FluFlipView` 자체에 공개적으로 호출하도록 의도된 고유 메소드는 없습니다. 페이지 전환은 `currentIndex` 프로퍼티를 직접 변경하거나, 사용자가 내부의 이전/다음 버튼 또는 마우스 휠을 사용함으로써 이루어집니다.

### 고유 시그널

`FluFlipView` 자체에서 정의된 고유 시그널은 없습니다. `currentIndex` 프로퍼티의 변경을 감지하려면 표준 `onCurrentIndexChanged` 시그널 핸들러를 사용할 수 있습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    spacing: 20
    width: 400

    FluText { text: "수평 플립 뷰" }
    FluFlipView {
        width: parent.width
        height: 300
        
        // content 프로퍼티에 표시할 항목들을 나열합니다.
        Image {
            source: "qrc:/example/res/image/banner_1.jpg"
            asynchronous: true
            fillMode: Image.PreserveAspectCrop
        }
        Image {
            source: "qrc:/example/res/image/banner_2.jpg"
            asynchronous: true
            fillMode: Image.PreserveAspectCrop
        }
        Rectangle {
            color: "lightblue"
            width: parent.width
            height: parent.height
            FluText { anchors.centerIn: parent; text: "페이지 3" }
        }
    }

    FluText { text: "수직 플립 뷰"; Layout.topMargin: 20 }
    FluFlipView {
        width: parent.width
        height: 300
        vertical: true // 수직 방향 설정

        Image {
            source: "qrc:/example/res/image/banner_3.jpg"
            asynchronous: true
            fillMode: Image.PreserveAspectCrop
        }
        Rectangle {
            color: "lightgreen"
            width: parent.width
            height: parent.height
            FluText { anchors.centerIn: parent; text: "세로 페이지 2" }
        }
    }
}
```

### 참고 사항

*   **탐색 방법**: 사용자는 `FluFlipView` 양 끝에 표시되는 화살표 버튼을 클릭하거나, 마우스 포인터가 `FluFlipView` 영역 위에 있을 때 마우스 휠을 스크롤하여 항목 간을 이동할 수 있습니다. 마우스 휠 스크롤 시에는 짧은 시간 내에 너무 빠르게 페이지가 넘어가는 것을 방지하기 위한 내부 타이머(약 250ms)가 작동합니다.
*   **직접 스와이프 비활성화**: 내부 `SwipeView`의 `interactive` 속성이 `false`로 설정되어 있어, 사용자가 터치나 마우스 드래그로 직접 콘텐츠를 스와이프하여 넘길 수는 없습니다.
*   **버튼 자동 숨김**: 첫 번째 항목에서는 '이전' 버튼이, 마지막 항목에서는 '다음' 버튼이 자동으로 숨겨집니다.
*   **콘텐츠 배치**: `FluFlipView` 태그 내부에 표시하고자 하는 QML Item들을 순서대로 배치하면 됩니다. 이 항목들이 `content` 프로퍼티를 통해 내부 `SwipeView`에 전달됩니다. 