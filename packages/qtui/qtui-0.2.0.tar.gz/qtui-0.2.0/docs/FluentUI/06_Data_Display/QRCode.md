# Fluent UI QR 코드 (FluQRCode)

이 문서에서는 `FluentUI` 모듈에서 제공하는 QR 코드 표시 컴포넌트인 `FluQRCode`에 대해 설명합니다. 이 컴포넌트는 주어진 텍스트 데이터를 QR(Quick Response) 코드로 변환하여 QML 인터페이스 내에 쉽게 시각화할 수 있도록 돕습니다.

내부적으로는 `FluQrCodeItem.py`라는 Python 클래스(`QQuickPaintedItem` 기반)를 사용하며, QR 코드 이미지 생성에는 Python의 `qrcode` 라이브러리(및 `Pillow` 라이브러리)가 필요합니다.

## 공통 임포트 방법

`FluQRCode` 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluQRCode

`FluQRCode`는 QML에서 간단하게 QR 코드를 생성하고 표시하기 위한 아이템입니다. 복잡한 이미지 생성 로직은 내부 Python 클래스에 위임하고, QML 레벨에서는 텍스트 입력, 색상 지정, 크기 및 여백 조절과 같은 주요 파라미터만 설정하면 됩니다.

### 기반 클래스

`Item` (from `QtQuick`)

### 주요 프로퍼티

| 이름      | 타입     | 기본값          | 설명                                                                                                  |
| :-------- | :------- | :-------------- | :---------------------------------------------------------------------------------------------------- |
| `text`    | `string` | `""`            | QR 코드로 인코딩될 텍스트 데이터입니다. 이 값이 변경되면 QR 코드 이미지가 자동으로 업데이트됩니다. (내부 `FluQrCodeItem.text` 별칭) |
| `color`   | `color`  | `Qt.rgba(0,0,0,1)` | QR 코드의 모듈(검은색 사각형 부분) 색상입니다. (내부 `FluQrCodeItem.color` 별칭)                               |
| `bgColor` | `color`  | `Qt.rgba(1,1,1,1)` | QR 코드의 배경색입니다. (내부 `FluQrCodeItem.bgColor` 별칭)                                         |
| `size`    | `int`    | `50`            | `FluQRCode` 아이템 전체의 너비와 높이 (픽셀 단위)입니다. 이 크기 내부에 QR 코드 이미지가 그려집니다.                            |
| `margins` | `int`    | `0`             | `FluQRCode` 아이템의 테두리와 실제 그려지는 QR 코드 이미지 사이의 여백 (픽셀 단위)입니다. 실제 QR 코드 이미지의 크기는 `size - margins`가 됩니다. |

### 고유 메소드

`FluQRCode` 컴포넌트에는 QML에서 직접 호출할 수 있는 고유 메소드가 없습니다.

### 고유 시그널

`FluQRCode` 컴포넌트에는 QML에서 직접 연결하여 사용할 수 있는 고유 시그널이 없습니다.

---

## FluQrCodeItem (내부 Python 클래스)

`FluQRCode.qml`은 화면에 QR 코드를 그리기 위해 내부적으로 `FluQrCodeItem.py`에 정의된 Python 클래스를 사용합니다.

*   **기반 클래스**: `QQuickPaintedItem` (from `PySide6.QtQuick`)
*   **주요 역할**: QML로부터 `text`, `color`, `bgColor`, `size` 프로퍼티 값을 받아 Python의 `qrcode` 라이브러리를 호출하여 QR 코드 데이터를 생성하고, `Pillow` 라이브러리를 통해 이미지를 생성한 뒤, `paint()` 메소드에서 `QPainter`를 사용하여 해당 이미지를 `Canvas`에 그립니다.
*   **라이브러리 의존성**: 이 Python 클래스는 `qrcode`와 `Pillow` 라이브러리가 설치되어 있어야 정상적으로 동작합니다 (`pip install qrcode[pil]`).
*   **QR 코드 설정**: 내부적으로 QR 코드 생성 시 버전은 가변적(`fit=True`), 에러 정정 레벨은 'H'(High, 약 30% 복원 가능), 테두리(border)는 0으로 고정되어 있습니다.

일반적으로 개발자는 `FluQRCode.qml` 컴포넌트를 사용하면 되며, `FluQrCodeItem.py`의 내부 구현을 직접 다룰 필요는 없습니다.

---

## 예제

다음은 `FluTextBox`에서 입력받은 텍스트를 `FluQRCode`로 표시하고, `FluColorPicker`와 `FluSlider`를 이용해 QR 코드의 색상, 크기, 여백을 동적으로 변경하는 예제입니다 (`T_QRCode.qml` 기반).

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    anchors.centerIn: parent
    spacing: 15

    FluQRCode {
        id: qrCode
        size: sizeSlider.value // 슬라이더 값으로 크기 조절
        text: textBox.text // 텍스트 박스 내용으로 QR 코드 생성
        color: colorPicker.current // 색상 선택기로 전경색 조절
        bgColor: bgColorPicker.current // 색상 선택기로 배경색 조절
        margins: marginsSlider.value // 슬라이더 값으로 여백 조절
        Layout.alignment: Qt.AlignHCenter
    }

    RowLayout {
        FluText { text: "Text:"; Layout.alignment: Qt.AlignVCenter }
        FluTextBox { id: textBox; text: "Hello Fluent UI!"; Layout.preferredWidth: 200 }
    }

    RowLayout {
        FluText { text: "Color:"; Layout.alignment: Qt.AlignVCenter }
        FluColorPicker { id: colorPicker; current: Qt.rgba(0,0,0,1) }
    }
    
    RowLayout {
        FluText { text: "BG Color:"; Layout.alignment: Qt.AlignVCenter }
        FluColorPicker { id: bgColorPicker; current: Qt.rgba(1,1,1,1) }
    }

    RowLayout {
        FluText { text: "Margins:"; Layout.alignment: Qt.AlignVCenter }
        FluSlider { id: marginsSlider; from: 0; to: 80; value: 0; Layout.preferredWidth: 150 }
        FluText { text: marginsSlider.value.toFixed(0) }
    }

    RowLayout {
        FluText { text: "Size:"; Layout.alignment: Qt.AlignVCenter }
        FluSlider { id: sizeSlider; from: 120; to: 300; value: 150; Layout.preferredWidth: 150 }
        FluText { text: sizeSlider.value.toFixed(0) }
    }
}
```

---

## 참고 사항

*   **Python 의존성**: `FluQRCode`를 사용하려면 애플리케이션 실행 환경에 `qrcode`와 `Pillow` Python 라이브러리가 설치되어 있어야 합니다. 터미널에서 다음 명령어를 사용하여 설치할 수 있습니다:
    ```bash
    pip install qrcode[pil]
    ```
*   **실제 QR 코드 크기**: 화면에 표시되는 QR 코드 이미지 자체의 크기는 `size` 프로퍼티가 아니라 `size - margins`입니다. `margins`는 QR 코드 주변의 빈 공간(배경색으로 채워짐)을 만듭니다.
*   **에러 정정 레벨**: QR 코드 생성 시 사용되는 에러 정정 레벨은 'H'(High)로 내부적으로 고정되어 있습니다. 이는 QR 코드 일부가 손상되어도 데이터를 복원할 수 있는 능력이 가장 높은 레벨입니다.
*   **텍스트 길이 제한**: QR 코드로 인코딩할 수 있는 텍스트의 양에는 제한이 있습니다. 너무 긴 텍스트를 `text` 프로퍼티에 입력하면 QR 코드가 생성되지 않을 수 있습니다. (내부 코드에는 1024 바이트 제한 로직이 존재하지만, 정확한 제한은 데이터 종류에 따라 달라질 수 있습니다.) 